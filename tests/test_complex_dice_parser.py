import sys

sys.path.append(".")

from app.library.complex_dice_parser import *


def test_init_with_number_token():
    description = "3d6"
    parser = Parser(description)
    assert parser.input_string == description
    assert parser.stack == ""
    assert parser.tokens_found == [(ParsingState.NUMBER, 3), (ParsingState.SIDES, 6)]


def test_init_with_operator_token():
    description = "3d6+2"
    parser = Parser(description)
    assert parser.input_string == description
    assert parser.stack == ""
    assert parser.tokens_found == [
        (ParsingState.NUMBER, 3),
        (ParsingState.SIDES, 6),
        (ParsingState.POOL_BONUS, 2),
    ]


def test_init_with_invalid_token():
    description = "3d6@2"
    try:
        parser = Parser(description)
    except ValueError as e:
        assert str(e) == "Unknown token @"
    else:
        assert False, "Expected ValueError to be raised"


def test_init_with_empty_description():
    description = ""
    parser = Parser(description)
    assert parser.input_string == description
    assert parser.stack == ""
    assert parser.tokens_found == []


def test_init_with_single_digit_number():
    description = "1d6"
    parser = Parser(description)
    assert parser.input_string == description
    assert parser.stack == ""
    assert parser.tokens_found == [(ParsingState.NUMBER, 1), (ParsingState.SIDES, 6)]


def test_init_with_multiple_digits_number():
    description = "10d6"
    parser = Parser(description)
    assert parser.input_string == description
    assert parser.stack == ""
    assert parser.tokens_found == [(ParsingState.NUMBER, 10), (ParsingState.SIDES, 6)]


def test_init_with_highest_2():
    description = "4d6h2"
    parser = Parser(description)
    assert parser.input_string == description
    assert parser.stack == ""
    assert parser.tokens_found == [
        (ParsingState.NUMBER, 4),
        (ParsingState.SIDES, 6),
        (ParsingState.HIGHEST, 2),
    ]
