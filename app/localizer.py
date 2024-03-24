import ast
import json
import pathlib
import re
from string import Template
from typing import Optional

import colorama

regex_only_letters = re.compile("[^a-zA-Z]")


def find_curly_brackets_content(input_string):
    # Regular expression pattern to find content within curly brackets
    pattern = r"\{(.*?)\}"
    # Find all occurrences of content within curly brackets
    return [str(content) for content in re.findall(pattern, input_string)]


def find_and_iterate_strings(line):
    # Regular expression pattern to find strings
    pattern = r"\'(?:\\.|[^\\\'])*\'|\"(?:\\.|[^\\\"])*\""
    # Find all occurrences of strings
    return [str(content) for content in re.findall(pattern, line)]


translation_data: dict[str, dict[str, str]] = json.loads(
    pathlib.Path("app", "localisable_data.json").read_text(encoding="utf-8")
)


def translations(key):
    return {
        "german": translation_data[key]["de"].lower().replace(" ", "_"),
        "english_us": translation_data[key]["en"].lower().replace(" ", "_"),
        "english_uk": translation_data[key]["en"].lower().replace(" ", "_"),
    }


def translate(locale: str, key: str, **kwargs):
    return translation_data[key][locale].format(**kwargs)


def generate_localisations(file_name: str):
    source_code = pathlib.Path("app", "exts", file_name).read_text(encoding="utf-8")
    localisable_data = json.loads(
        pathlib.Path("app", "localisable_data.json").read_text(encoding="utf-8")
    )

    def get_decorator_localization(decorator: ast.expr):
        if not isinstance(decorator, ast.Call):
            return
        decorator_name = str(decorator)
        try:
            decorator_name = (
                decorator.func.id if isinstance(decorator.func, ast.Name) else decorator.func.attr
            )
            decorator_keywords = [keyword.arg for keyword in decorator.keywords]
            decorator_keywords_values = [keyword.value.value for keyword in decorator.keywords]
            if "name" in decorator_keywords and "description" in decorator_keywords:
                localisable_data[
                    decorator_keywords_values[decorator_keywords.index("name")] + "_description"
                ] = {
                    "de": "",
                    "en": decorator_keywords_values[decorator_keywords.index("description")],
                }
        except Exception as e:
            print(colorama.Fore.RED, f"Error: {e}")
            print(f"\t{decorator.lineno} {decorator_name}", colorama.Style.RESET_ALL)

    tree = ast.parse(source_code)
    for item in ast.walk(tree):
        if isinstance(item, ast.AsyncFunctionDef):
            for decorator in item.decorator_list:
                get_decorator_localization(decorator)

    pathlib.Path("app", "localisable_data.json").write_text(
        json.dumps(localisable_data, indent=4), encoding="utf-8"
    )
    localize_source_code(file_name, localisable_data)


def localize_source_code(file_name: str, localisable_data: dict[str, dict[str, str]]):
    source_code = pathlib.Path("app", "exts", file_name).read_text(encoding="utf-8")
    if "from interactions import LocalisedDesc" not in source_code:
        source_code = "from interactions import LocalisedDesc\n" + source_code
    if "import app.localizer as localizer" not in source_code:
        source_code = "import app.localizer as localizer\n" + source_code
    for key, translation_values in localisable_data.items():
        source_code = source_code.replace(
            "'" + translation_values["en"] + "'",
            f"LocalisedDesc(**localizer.translations('{key}'))",
        )
        source_code = source_code.replace(
            '"' + translation_values["en"] + '"',
            f"LocalisedDesc(**localizer.translations('{key}'))",
        )
    pathlib.Path("app", "exts", file_name).write_text(source_code, encoding="utf-8")


def keyify(string: str):
    unwanted_chars = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"
    return (
        "".join([char for char in string if char not in unwanted_chars]).replace(" ", "_").lower()
    )


def localize_line(
    line: str, current_string: str, is_in_decorator: bool = False
) -> tuple[str, dict[str, dict[str, str]], str]:
    interpolations = {}
    interpolated_string = current_string
    remaining_string = current_string
    for interpolated_content in find_curly_brackets_content(current_string):
        interpolations[keyify(interpolated_content)] = interpolated_content
    if interpolations:
        interpolation_kwargs = ", " + ",".join(
            [f"{key}={value}" for key, value in interpolations.items()]
        )
        for key, value in interpolations.items():
            interpolated_string = interpolated_string.replace(f"{{{value}}}", f"{{{key}}}")
            remaining_string = remaining_string.replace(f"{{{value}}}", "")
    else:
        interpolation_kwargs = ""
    if is_in_decorator:
        if f'name={current_string.replace(" ","")}' in line.replace(" ", ""):
            replacement = f"LocalisedName(**localizer.translations('{keyify(current_string)}'))"
        elif f'description={current_string.replace(" ","")}' in line.replace(" ", ""):
            replacement = f"LocalisedDesc(**localizer.translations('{keyify(current_string)}'{interpolation_kwargs}))"
        else:
            replacement = current_string
            print(
                colorama.Fore.RED,
                f"Error: {line}",
                "could not find name or description",
                colorama.Style.RESET_ALL,
            )
    else:
        replacement = (
            f"localizer.translate(ctx.locale,'{keyify(current_string)}'{interpolation_kwargs})"
        )
    return (
        line.replace(f"f{current_string}", replacement).replace(f"{current_string}", replacement),
        {keyify(current_string): {"de": "", "en": interpolated_string.strip("'\"")}},
        replacement,
        len(regex_only_letters.sub("", remaining_string)) > 2,
    )


def highlight_string(
    line: str,
    highlight: str,
    base_color: str = colorama.Fore.BLUE,
    warn_keywords: Optional[list[str]] = None,
):
    if not warn_keywords:
        warn_keywords = ["name=", "description=", "localizer", "print", "custom_id"]
    if warn_keywords:
        for keyword in warn_keywords:
            line = line.replace(keyword, colorama.Fore.RED + keyword + base_color)
    return line.replace(highlight, colorama.Fore.GREEN + highlight + base_color)


def show_line_with_scope(
    lines: dict[int, str],
    line_number: int,
    scope: int,
    base_color: str = colorama.Fore.BLUE,
    line_overwrite: Optional[str] = None,
):
    for i in range(line_number - scope, line_number + scope):
        if i in lines:
            if i == line_number:
                print(f"{base_color}{i}: {line_overwrite or lines[i]}")
            else:
                print(f"{i}: {lines[i]}")
            print(colorama.Style.RESET_ALL, end="")


def interactive_localization(file_name: str):
    source_code = pathlib.Path("app", "exts", file_name).read_text(encoding="utf-8")
    localisable_data: dict[str, dict[str, str]] = json.loads(
        pathlib.Path("app", "localisable_data.json").read_text(encoding="utf-8")
    )
    lines = dict(enumerate(source_code.split("\n")))
    lines_with_string = [
        line_number
        for line_number, line in enumerate(source_code.split("\n"))
        if '"' in line
        or "'" in line
        and any(len(keyify(string)) > 2 for string in find_and_iterate_strings(line))
    ]
    scope: int = 3
    for idx, line_number in enumerate(lines_with_string):
        progress_percent = idx / len(lines_with_string)
        progress_bar = "#" * (int(progress_percent * 10)) + "-" * (10 - int(progress_percent * 10))
        print(f"\n\nProgress: {idx}/{len(lines_with_string)}  ", progress_bar)
        handling_line = True
        while handling_line:
            for current_string in find_and_iterate_strings(lines[line_number]):
                if lines[line_number].strip().startswith('"""') or lines[
                    line_number
                ].strip().startswith("'''"):
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping string in comment")
                    continue
                if len(keyify(current_string)) < 3:
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping short string")
                    continue
                if (
                    f"translations({current_string})" in lines[line_number]
                    or f"translate(ctx.locale,{current_string}" in lines[line_number]
                    or f"translate(ctx.locale,f{current_string}" in lines[line_number]
                ):
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping already localized string")
                    continue
                # if f'name={current_string}' in lines[line_number] and 'slash_option' in lines[line_number-1]+lines[line_number] or 'slash_command'  in lines[line_number-1]+lines[line_number]:
                #     show_line_with_scope(lines,line_number,1,line_overwrite=highlight_string(lines[line_number],current_string,base_color=colorama.Fore.YELLOW),base_color=colorama.Fore.YELLOW)
                #     print(">> Skipping name string")
                #     continue
                if f"custom_id={current_string}" in lines[line_number]:
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping custom_id string")
                    continue
                if (
                    f"print({current_string})" in lines[line_number]
                    or f"print(f{current_string})" in lines[line_number]
                ):
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping print string")
                    continue
                if f".autocomplete({current_string})" in lines[line_number]:
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping autocomplete string")
                    continue
                (
                    localized_line,
                    translation_entry,
                    replacement,
                    has_letters_to_translate,
                ) = localize_line(lines[line_number], current_string)
                localized_line_dec, translation_entry_dec, replacement_dec, _ = localize_line(
                    lines[line_number], current_string, True
                )
                if not has_letters_to_translate:
                    show_line_with_scope(
                        lines,
                        line_number,
                        1,
                        line_overwrite=highlight_string(
                            lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                        ),
                        base_color=colorama.Fore.YELLOW,
                    )
                    print(">> Skipping string without letters to translate")
                    continue
                show_line_with_scope(
                    lines,
                    line_number,
                    scope,
                    line_overwrite=highlight_string(lines[line_number], current_string),
                )
                print("=====================================")
                print(
                    f"Enter to accept suggestion, or 'n' to skip, 'f' to Flag for later inspection, or 'q' to quit, + or - to change scope ({scope})"
                )
                print("=====================================")
                print("Python:")
                show_line_with_scope(
                    lines,
                    line_number,
                    scope,
                    line_overwrite=highlight_string(
                        localized_line, replacement, warn_keywords=["XYZ"]
                    ),
                )
                print("=====================================")
                print("Python (Decorator):")
                show_line_with_scope(
                    lines,
                    line_number,
                    scope,
                    line_overwrite=highlight_string(
                        localized_line_dec,
                        replacement_dec,
                        warn_keywords=["XYZ"],
                        base_color=colorama.Fore.YELLOW,
                    ),
                    base_color=colorama.Fore.YELLOW,
                )
                print("=====================================")
                print("Translation:")
                print(json.dumps(translation_entry, indent=4))
                print("=====================================")
                user_input = input()
                if user_input in "f":
                    lines[line_number] += "#TODO: LOCALIZATION FLAG"
                    localized_line += "#TODO: LOCALIZATION FLAG"
                    localized_line_dec += "#TODO: LOCALIZATION FLAG"
                    user_input.replace("f", "")
                if user_input == "q":
                    return
                if user_input == "n":
                    continue
                if user_input == "+":
                    scope += 1
                    break
                if user_input == "-":
                    scope -= 1
                    break
                if user_input == "":
                    localisable_data |= translation_entry
                    lines[line_number] = localized_line
                    break
                if user_input == "d":
                    localisable_data |= translation_entry_dec
                    lines[line_number] = localized_line_dec
                    break
            else:
                handling_line = False
    pathlib.Path("app", "exts", file_name).write_text(
        "\n".join([lines[i] for i in sorted(lines.keys())]), encoding="utf-8"
    )
    pathlib.Path("app", "localisable_data.json").write_text(
        json.dumps(localisable_data, indent=4), encoding="utf-8"
    )


if __name__ == "__main__":
    for file_name in pathlib.Path("app", "exts").iterdir():
        if file_name.is_file() and file_name.suffix == ".py":
            print("=" * (len(file_name.name) + 2))
            print(f"|{file_name.name}|")
            print("=" * (len(file_name.name) + 2))
            localise = input("Localize? (y/n)")
            if localise != "y":
                continue

            generate_localisations(file_name.name)
            print("Starting interactive localization")
            input("Press enter to start")
            interactive_localization(file_name.name)
