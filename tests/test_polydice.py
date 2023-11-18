import sys

sys.path.append(".")

from app.library.complex_dice_parser import Parser
from app.library.polydice import *


def test_roll_dice_basic():
    results = roll_dice_basic(number=3, sides=6, dice_modifier=2)
    assert len(results) == 3
    for result in results:
        assert 1 <= result.result <= 6
        assert result.dice_modifier == 2


def test_roll_dice_sum():
    result = roll_dice_sum(
        number=3, sides=6, high_exploding=ExplodingBehavior.NONE, dice_modifier=0, pool_modifier=2
    )
    assert isinstance(result, DicePoolResultSum)
    assert result.sum >= 3 and result.sum <= 20


def test_roll_dice_successes():
    result = roll_dice_successes(
        number=5,
        sides=10,
        high_exploding=ExplodingBehavior.NONE,
        low_subtracion=False,
        dice_modifier=0,
        pool_modifier=0,
        threshold=7,
    )
    assert isinstance(result, DicePoolResultSuccesses)
    assert result.successes >= 0 and result.successes <= 5


def test_roll_dice_successes_with_low_subtraction():
    result = roll_dice_successes(
        number=10,
        sides=6,
        high_exploding=ExplodingBehavior.NONE,
        low_subtracion=True,
        dice_modifier=0,
        pool_modifier=0,
        threshold=7,
    )
    assert isinstance(result, DicePoolResultSuccesses)
    assert result.successes >= -10 and result.successes <= 10


def test_roll_dice_exploding_once():
    original_dice, extra_dice = roll_pool(
        number=3, sides=6, dice_modifier=0, high_exploding=ExplodingBehavior.ONCE
    )
    assert len(original_dice) >= 3
    assert len(extra_dice) >= 0


def test_roll_dice_exploding_cascading():
    original_dice, extra_dice = roll_pool(
        number=60, sides=6, dice_modifier=0, high_exploding=ExplodingBehavior.CASCADING
    )
    assert len(original_dice) >= 3
    assert len(extra_dice) >= 0


def test_roll_dice():
    # Test scenario 1: Roll 2 six-sided dice with no modifiers
    complex_pool = Parser("2d6").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) == 2
    assert all(1 <= dice_result.result <= 6 for dice_result in result.dice_results)


def test_roll_dice_with_modifiers():
    # Test scenario 2: Roll 3 ten-sided dice with a dice modifier of +2
    complex_pool = Parser("3d10++2").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) == 3
    assert all(
        3 <= dice_result.value <= 12 for dice_result in result.dice_results
    ), f"Expected all dice results to be between 3 and 12, got {result.formatted()}"


def test_roll_dice_with_exploding_behavior():
    # Test scenario 3: Roll 4 eight-sided dice with cascading exploding behavior
    complex_pool = Parser("4d8!!").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) >= 4
    assert all(1 <= dice_result.result <= 8 for dice_result in result.dice_results)


def test_roll_dice_with_pool_modifier():
    # Test scenario 4: Roll 5 four-sided dice with a pool modifier of +3
    complex_pool = Parser("5d4+3").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) == 5
    assert all(1 <= dice_result.result <= 4 for dice_result in result.dice_results)
    assert isinstance(result, DicePoolExclusionsSum)
    assert result.sum >= 8 and result.sum <= 23


def test_roll_dice_with_success_threshold():
    # Test scenario 5: Roll 6 twelve-sided dice with a success threshold of 8
    complex_pool = Parser("6d12s8").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) == 6
    assert all(1 <= dice_result.result <= 12 for dice_result in result.dice_results)
    assert isinstance(
        result, DicePoolExclusionsSuccesses
    ), f"Expected DicePoolExclusionsSuccesses, got {type(result).__name__}"
    assert result.successes >= 0 and result.successes <= 6


def test_roll_dice_with_failure_threshold():
    # Test scenario 6: Roll 7 twenty-sided dice with a failure threshold of 5
    complex_pool = Parser("7d20f5s18").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) == 7
    assert all(1 <= dice_result.result <= 20 for dice_result in result.dice_results)
    assert isinstance(result, DicePoolExclusionsSuccesses)
    assert result.successes >= -7 and result.successes <= 7


def test_roll_dice_with_high_limit():
    # Test scenario 7: Roll 8 six-sided dice and keep the 3 highest values
    complex_pool = Parser("23d6h3").build_pool()
    result = complex_pool.roll()
    assert len(result.dice_results) == 23
    assert isinstance(result, DicePoolExclusionsSum)
    assert len(result.excluded) == len(result.dice_results) - 3, result.formatted()
    assert all(1 <= dice_result.result <= 6 for dice_result in result.dice_results)
    assert result.sum >= 3 and result.sum <= 18
