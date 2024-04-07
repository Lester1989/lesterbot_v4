import sys

sys.path.append(".")

from app.library.complex_dice_parser import Parser
from app.library.polydice import *
from app.library.charsheet import RuleSystemRolls

def test_roll_dice_basic():
    roll = RuleSystemRolls(rule_system="testsystem",name="ini",roll="2d6")
    assert len(roll.needed_sheet_values) == 0

    roll = RuleSystemRolls(rule_system="testsystem",name="ini",roll="{attribute1}d6+2")
    assert len(roll.needed_sheet_values) == 1
    assert roll.needed_sheet_values[0] == "attribute1",roll.needed_sheet_values

    evaluated = roll.eval({"attribute1":3})
    assert evaluated == "3d6+2",evaluated

    roll = RuleSystemRolls(rule_system="testsystem",name="ini",roll="{attribute1+attribute2}d6+2")
    assert len(roll.needed_sheet_values) == 2
    assert "attribute1" in roll.needed_sheet_values ,roll.needed_sheet_values
    assert "attribute2" in roll.needed_sheet_values ,roll.needed_sheet_values

    evaluated = roll.eval({"attribute1":3,"attribute2":2})
    assert evaluated == "5d6+2",evaluated

    roll = RuleSystemRolls(rule_system="testsystem",name="ini",roll="{(attribute1+attribute2)*2}d6+2")
    assert len(roll.needed_sheet_values) == 2
    assert "attribute1" in roll.needed_sheet_values ,roll.needed_sheet_values
    assert "attribute2" in roll.needed_sheet_values ,roll.needed_sheet_values

    evaluated = roll.eval({"attribute1":3,"attribute2":2})
    assert evaluated == "10d6+2",evaluated

    pool = Parser(evaluated).build_pool()
    assert pool.number == 10
    assert pool.sides == 6
    assert pool.pool_modifier == 2


