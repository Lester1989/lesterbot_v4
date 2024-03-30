"""
This module provides functions to localize strings.

You can also run this script to localize strings in the source code interactively.
"""

import ast
from enum import Enum
import json
import pathlib
import re
from typing import Optional

import colorama

regex_only_letters = re.compile("[^a-zA-Z]")


def find_curly_brackets_content(input_string):
    """
    Find all content within curly brackets in a string.

    Parameters:
    -----------
    input_string : str
        The string to search for content within curly brackets.

    Returns:
    --------
    list[str]
        A list of all content within curly brackets.
    """
    # Regular expression pattern to find content within curly brackets
    pattern = r"\{(.*?)\}"
    return [str(content) for content in re.findall(pattern, input_string)]


def find_and_iterate_strings(line):
    """
    Find all strings in a line of code and iterate over them.

    Parameters:
    -----------
    line : str
        The line of code to search for strings.

    Returns:
    --------
    list[str]
        A list of all strings in the line of code.
    """
    # Regular expression pattern to find strings
    pattern = r"\'(?:\\.|[^\\\'])*\'|\"(?:\\.|[^\\\"])*\""
    return [str(content) for content in re.findall(pattern, line)]


translation_data: dict[str, dict[str, str]] = json.loads(
    pathlib.Path("app", "localisable_data.json").read_text(encoding="utf-8")
)


def translations(key:str):
    """
    Get translations for a key.

    Parameters:
    -----------
    key : str
        The key to get translations for.

    Returns:
    --------
    dict[str, str]
        A dictionary with translations for the key.
    """
    return {
        "german": translation_data[key]["de"].lower().replace(" ", "_"),
        "english_us": translation_data[key]["en"].lower().replace(" ", "_"),
        "english_uk": translation_data[key]["en"].lower().replace(" ", "_"),
    }


def translate(locale: str, key: str, **kwargs):
    """
    Translate a key to a locale.

    Parameters:
    -----------
    locale : str
        The locale to translate the key to.
    key : str
        The key to translate.
    **kwargs
        Additional keyword arguments replacing placeholders in the translation.

    Returns:
    --------
    str
        The translated string.
    """
    if locale in {"german", "de"}:
        return translation_data[key]["de"].format(**kwargs)
    return translation_data[key]["en"].format(**kwargs)


def generate_localisations(file_name: str):
    """
    Generate localisations for a file.
    opens the file and searches for decorators with name and description keywords
    and adds them to the localisable_data.json file.

    Parameters:
    -----------
    file_name : str
        The name of the file to generate localisations for.
    """
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
    """
    Localize the source code of a file.

    Parameters:
    -----------
    file_name : str
        The name of the file to localize.
    localisable_data : dict[str, dict[str, str]]
        The localisable data to use for localizing the source code.
    """
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
    """
    Convert a string to a key by removing unwanted characters and replacing spaces with underscores.

    Parameters:
    -----------
    string : str
        The string to convert to a key.

    Returns:
    --------
    str
        The keyified string.
    """
    unwanted_chars = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"
    return (
        "".join([char for char in string if char not in unwanted_chars]).replace(" ", "_").lower()
    )


def localize_line( line: str, current_string: str, is_in_decorator: bool = False ):
    """
    Localize a line of code.

    Parameters:
    -----------
    line : str
        The line of code to localize.
    current_string : str
        The current string to localize.
    is_in_decorator : bool
        Whether the string is in a decorator.

    Returns:
    --------
    tuple[str, dict[str, dict[str, str]], str, bool]
        A tuple containing the localized line, the translation entry, the replacement string, and whether there are (more than 2) letters to translate.
    """
    interpolated_string = current_string
    remaining_string = current_string
    if interpolations := {
        keyify(interpolated_content): interpolated_content
        for interpolated_content in find_curly_brackets_content(current_string)
    }:
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
    """
    Highlight a string in a line of code.

    Parameters:
    -----------
    line : str
        The line of code to highlight the string in.
    highlight : str
        The string to highlight.
    base_color : str
        The base color to use for highlighting.
    warn_keywords : list[str]
        A list of keywords to warn about in the line of code.

    Returns:
    --------
    str
        The line of code with the string highlighted.
    """
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
    """
    Show a line of code with a scope of surrounding lines.

    Parameters:
    -----------
    lines : dict[int, str]
        A dictionary of line numbers and lines of code.
    line_number : int
        The line number to show.
    scope : int
        The scope of surrounding lines to show.
    base_color : str
        The base color to use for highlighting.
    line_overwrite : str
        The line to overwrite the original line with.
    """
    for i in range(line_number - scope, line_number + scope):
        if i in lines:
            if i == line_number:
                print(f"{base_color}{i}: {line_overwrite or lines[i]}")
            else:
                print(f"{i}: {lines[i]}")
            print(colorama.Style.RESET_ALL, end="")



def interactive_localization(file_name: str):
    """
    Interactively localize a file.

    Parameters:
    -----------
    file_name : str
        The name of the file to localize.
    """
    localisable_data, lines, lines_with_string = load_data(file_name)
    scope: int = 3
    for idx, line_number in enumerate(lines_with_string):
        progress_percent = idx / len(lines_with_string)
        progress_bar = "#" * (int(progress_percent * 10)) + "-" * (10 - int(progress_percent * 10))
        print(f"\n\nProgress: {idx}/{len(lines_with_string)}  ", progress_bar)
        handling_line = True
        while handling_line:
            for current_string in find_and_iterate_strings(lines[line_number]):
                current_string_needs_translation = check_auto_skip_line(lines, line_number, current_string)
                if not current_string_needs_translation:
                    continue
                localized_line, translation_entry, replacement, has_letters_to_translate = localize_line(lines[line_number], current_string)
                localized_line_dec, translation_entry_dec, replacement_dec, _ = localize_line( lines[line_number], current_string, True )
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
                show_suggested_refactoring(lines, scope, line_number, localized_line, translation_entry, replacement, localized_line_dec, replacement_dec, current_string)
                loop_control = handle_user_interaction(lines, scope, line_number, localized_line, translation_entry, localized_line_dec, translation_entry_dec, localisable_data)
                if loop_control == LoopControl.RETURN:
                    return
                if loop_control == LoopControl.CONTINUE:
                    continue
                if loop_control == LoopControl.BREAK:
                    break
            else:
                handling_line = False
    save_data(file_name, localisable_data, lines)

def save_data(file_name:str, localisable_data:dict[str, dict[str, str]], lines:dict[int,str]):
    """
    Save data to a file.

    Parameters:
    -----------
    file_name : str
        The name of the file to save data to, in the app/exts directory.
    localisable_data : dict[str, dict[str, str]]
        The localisable data to save.
    lines : dict[int, str]
        The lines of code to save.
    """
    pathlib.Path("app", "exts", file_name).write_text(
        "\n".join([lines[i] for i in sorted(lines.keys())]), encoding="utf-8"
    )
    pathlib.Path("app", "localisable_data.json").write_text(
        json.dumps(localisable_data, indent=4), encoding="utf-8"
    )

def load_data(file_name:str):
    """
    Load data from a file.

    Parameters:
    -----------
    file_name : str
        The name of the file to load data from, in the app/exts directory.

    Returns:
    --------
    dict[str, dict[str, str]], dict[int, str], list[int]
        The localisable data, the lines of code, and the lines with strings.
    """
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
    return localisable_data,lines,lines_with_string

class LoopControl(Enum):
    """ Loop control actions. """
    CONTINUE = "continue"
    BREAK = "break"
    RETURN = "return"

def handle_user_interaction(lines:dict[int,str], scope:int, line_number:int, localized_line:str, translation_entry:str, localized_line_dec:str, translation_entry_dec:str, localisable_data:dict[str, dict[str, str]]):
    """
    Handle user interaction for a line of code.

    Parameters:
    -----------
    lines : dict[int, str]
        A dictionary of line numbers and lines of code.
    scope : int
        The scope of surrounding lines.
    line_number : int
        The line number to handle.
    localized_line : str
        The localized line to handle.
    translation_entry : str
        The translation entry to handle.
    localized_line_dec : str
        The localized line with a decorator to handle.
    translation_entry_dec : str
        The translation entry with a decorator to handle.

    Returns:
    --------
    LoopControl
        The loop control action to take.
    """
    print("Action:".center(40, "="))
    print(f"Enter to accept suggestion, or 'n' to skip, 'f' to Flag for later inspection, or 'q' to quit, + or - to change scope ({scope})" )
    user_input = input()
    if user_input in "f":
        lines[line_number] += "#TODO: LOCALIZATION FLAG"
        localized_line += "#TODO: LOCALIZATION FLAG"
        localized_line_dec += "#TODO: LOCALIZATION FLAG"
        user_input.replace("f", "")
    if user_input == "q":
        return LoopControl.RETURN
    if user_input == "n":
        return LoopControl.CONTINUE
    if user_input == "+":
        scope += 1
        return LoopControl.BREAK
    if user_input == "-":
        scope -= 1
        return LoopControl.BREAK
    if user_input == "":
        localisable_data |= translation_entry
        lines[line_number] = localized_line
        # break
        return LoopControl.BREAK
    if user_input == "d":
        localisable_data |= translation_entry_dec
        lines[line_number] = localized_line_dec
        # break
        return LoopControl.BREAK
    return LoopControl.CONTINUE

def show_suggested_refactoring(lines:dict[int,str], scope:int, line_number:int, localized_line:str, translation_entry:str, replacement:str, localized_line_dec:str, replacement_dec:str,current_string:str):
    """
    Show suggested refactoring for a line of code.

    Parameters:
    -----------
    lines : dict[int, str]
        A dictionary of line numbers and lines of code.
    scope : int
        The scope of surrounding lines to show.
    line_number : int
        The line number to show.
    localized_line : str
        The localized line to show.
    translation_entry : str
        The translation entry to show.
    replacement : str
        The replacement string to show.
    localized_line_dec : str
        The localized line with a decorator to show.
    replacement_dec : str
        The replacement string with a decorator to show.
    current_string : str
        The current string to show.
    """
    print("Original:".center(40, "="))
    show_line_with_scope(
        lines,
        line_number,
        scope,
        line_overwrite=highlight_string(lines[line_number], current_string),
    )
    print("Python:".center(40, "="))
    show_line_with_scope(
                    lines,
                    line_number,
                    scope,
                    line_overwrite=highlight_string(
                        localized_line, replacement, warn_keywords=["XYZ"]
                    ),
                )
    print("Python (Decorator):".center(40, "="))
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
    print("Translation:".center(40, "="))
    print(json.dumps(translation_entry, indent=4))
    print("=====================================")

def check_auto_skip_line(lines, line_number, current_string,silent:bool=False):
    """
    Check if a line should be skipped automatically.

    Parameters:
    -----------
    lines : dict[int, str]
        A dictionary of line numbers and lines of code.
    line_number : int
        The line number to check.
    current_string : str
        The current string to check.
    silent : bool
        Whether to print messages.

    Returns:
    --------
    bool
        Whether the line should be skipped automatically.
    """
    checks_with_message=[
        (
            lambda current_string,line_number: lines[line_number].strip().startswith('"""') or lines[ line_number ].strip().startswith("'''"),
            ">> Skipping string in comment"
        ),
        (
            lambda current_string,line_number: len(keyify(current_string)) < 3,
            ">> Skipping short string"
        ),
        (
            lambda current_string,line_number: f"translations({current_string})" in lines[line_number]
            or f"translate(ctx.locale,{current_string}" in lines[line_number]
            or f"translate(ctx.locale,f{current_string}" in lines[line_number],
            ">> Skipping already localized string"
        ),
        (
            lambda current_string,line_number: f"custom_id={current_string}" in lines[line_number],
            ">> Skipping custom_id string"
        ),
        (
            lambda current_string,line_number: f"print({current_string})" in lines[line_number]
            or f"print(f{current_string})" in lines[line_number],
            ">> Skipping print string"
        ),
        (
            lambda current_string,line_number: f".autocomplete({current_string})" in lines[line_number],
            ">> Skipping autocomplete string"
        ),
    ]
    current_string_needs_translation = False
    for check, message in checks_with_message:
        if check(current_string,line_number):
            if not silent:
                show_line_with_scope(
                    lines,
                    line_number,
                    1,
                    line_overwrite=highlight_string(
                        lines[line_number], current_string, base_color=colorama.Fore.YELLOW
                    ),
                    base_color=colorama.Fore.YELLOW,
                )
                print(message)
            break
    else:
        current_string_needs_translation = True
    return current_string_needs_translation


if __name__ == "__main__":
    for ext_file_name in pathlib.Path("app", "exts").iterdir():
        if ext_file_name.is_file() and ext_file_name.suffix == ".py":
            print("=" * (len(ext_file_name.name) + 2))
            print(f"|{ext_file_name.name}|")
            print("=" * (len(ext_file_name.name) + 2))
            localise = input("Localize? (y/n)")
            if localise != "y":
                continue

            generate_localisations(ext_file_name.name)
            print("Starting interactive localization")
            input("Press enter to start")
            interactive_localization(ext_file_name.name)
