from app.library.polydice import *

def test_roll_dice_basic():
    results = roll_dice_basic(number=3, sides=6, dice_modifier=2)
    assert len(results) == 3
    for result in results:
        assert 1 <= result.result <= 6
        assert result.dice_modifier == 2

def test_roll_dice_sum():
    result = roll_dice_sum(number=3, sides=6, high_exploding=ExplodingBehavior.NONE, dice_modifier=0, pool_modifier=2)
    assert isinstance(result, DicePoolResultSum)
    assert result.sum >= 3 and result.sum <= 20

def test_roll_dice_successes():
    result = roll_dice_successes(number=5, sides=10, high_exploding=ExplodingBehavior.NONE, low_subtracion=False, dice_modifier=0, pool_modifier=0, threshold=7)
    assert isinstance(result, DicePoolResultSuccesses)
    assert result.successes >= 0 and result.successes <= 5

def test_roll_dice_successes_with_low_subtraction():
    result = roll_dice_successes(number=10, sides=6, high_exploding=ExplodingBehavior.NONE, low_subtracion=True, dice_modifier=0, pool_modifier=0, threshold=7)
    assert isinstance(result, DicePoolResultSuccesses)
    assert result.successes >= -10 and result.successes <= 10

def test_roll_dice_exploding_once():
    original_dice,extra_dice = roll_pool(number=3, sides=6, dice_modifier=0, high_exploding=ExplodingBehavior.ONCE)
    assert len(original_dice) >= 3
    assert len(extra_dice) >= 0


def test_roll_dice_exploding_cascading():
    original_dice,extra_dice = roll_pool(number=60, sides=6, dice_modifier=0, high_exploding=ExplodingBehavior.CASCADING)
    assert len(original_dice) >= 3
    assert len(extra_dice) >= 0


