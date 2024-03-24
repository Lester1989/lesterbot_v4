import re


def find_curly_brackets_content(input_string):
    # Regular expression pattern to find content within curly brackets
    pattern = r"\{(.*?)\}"

    # Find all occurrences of content within curly brackets
    matches = re.findall(pattern, input_string)

    return matches


# Example usage:
input_string = "This is {content} within {curly('brackets')}."
content_within_curly_brackets = find_curly_brackets_content(input_string)
print(content_within_curly_brackets)
