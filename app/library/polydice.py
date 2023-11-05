import random
from dataclasses import dataclass
from enum import Enum

class ExplodingBehavior(Enum):
    """
    Describes the behavior of dice that roll the maximum value. Maybe adding a new dice
    """
    NONE = 0
    ONCE = 1
    CASCADING = 2

@dataclass
class DiceResult:
    """
    Represents the result of a single dice roll.
    """
    sides: int
    dice_modifier: int
    result: int

    @property
    def is_max(self):
        """
        Returns True if the result is the maximum possible value for the dice.
        """
        return self.result == self.sides

@dataclass
class DicePoolResult:
    """
    Represents the result of a pool of dice rolls.
    """
    pool_modifier: int
    dice_results: list[DiceResult]
    extra_dice: list[DiceResult]


class DicePoolResultSum(DicePoolResult):
    """
    Represents the result of a pool of dice rolls where the final result is the sum of all the dice rolls.
    """
    @property
    def sum(self):
        """
        Returns the sum of all the dice rolls, including any modifiers.
        """
        return sum(
            dice.dice_modifier + dice.result
            for dice in self.dice_results
        ) + sum(
            dice.dice_modifier + dice.result
            for dice in self.extra_dice
        ) + self.pool_modifier

@dataclass
class DicePoolResultSuccesses(DicePoolResult):
    """
    Represents the result of a pool of dice rolls where the final result is the number of dice that rolled a value greater than or equal to the threshold.
    """
    successes:int



def roll_dice_basic(number:int=1, sides:int=6, dice_modifier:int=0):
    """
    Rolls a number of dice with the specified number of sides and modifier.

    Args:
        number (int): The number of dice to roll.
        sides (int): The number of sides on each dice.
        dice_modifier (int): The modifier to add to each dice roll.

    Returns:
        A list of DiceResult objects representing the result of each dice roll.
    """
    return [
        DiceResult(
            sides=sides,
            dice_modifier=dice_modifier,
            result=random.randint(1,sides)
        )
        for _ in range(number)
    ]

def roll_dice_sum(number:int=1, sides:int=6, high_exploding:ExplodingBehavior=ExplodingBehavior.NONE,dice_modifier:int=0,pool_modifier:int=0):
    """
    Rolls a number of dice and returns the sum of the results.

    Args:
        number (int): The number of dice to roll.
        sides (int): The number of sides on each dice.
        high_exploding (ExplodingBehavior): The exploding behavior for dice that roll the maximum value.
        dice_modifier (int): The modifier to add to each dice roll.
        pool_modifier (int): The modifier to add to the final result.

    Returns:
        A DicePoolResultSum object representing the result of the dice rolls.
    """
    original_dice, extra_dice = roll_pool(number, sides, high_exploding, dice_modifier)
    return DicePoolResultSum(
        pool_modifier=pool_modifier,
        dice_results=original_dice,
        extra_dice=extra_dice
    )

def roll_pool(number:int, sides:int, high_exploding:ExplodingBehavior, dice_modifier:int):
    """
    Rolls a number of dice and returns the sum of the results.

    Args:
        number (int): The number of dice to roll.
        sides (int): The number of sides on each dice.
        high_exploding (ExplodingBehavior): The exploding behavior for dice that roll the maximum value.
        dice_modifier (int): The modifier to add to each dice roll.
        pool_modifier (int): The modifier to add to the final result.
    """
    original_dice = roll_dice_basic(number=number, sides=sides, dice_modifier=dice_modifier)
    extra_dice = []
    if high_exploding != ExplodingBehavior.NONE:
        exploding_count = len([dice for dice in original_dice if dice.is_max])
        extra_dice = roll_dice_basic( number=exploding_count, sides=sides, dice_modifier=dice_modifier)
    if high_exploding == ExplodingBehavior.CASCADING:
        new_dice = extra_dice.copy()
        extra_dice = []
        while new_dice:
            current_dice = new_dice.pop()
            extra_dice.append(current_dice)
            if current_dice.is_max:
                new_dice.append(
                    DiceResult(
                        sides=sides,
                        dice_modifier=dice_modifier,
                        result=random.randint(1, sides),
                    )
                )
    return original_dice,extra_dice

def roll_dice_successes(number:int=1, sides:int=6, high_exploding:ExplodingBehavior=ExplodingBehavior.NONE, low_subtracion:bool=False,dice_modifier:int=0,pool_modifier:int=0,threshold:int=4):
    """
    Rolls a number of dice and returns the number of dice that rolled a value greater than or equal to the threshold.

    Args:
        number (int): The number of dice to roll.
        sides (int): The number of sides on each dice.
        high_exploding (ExplodingBehavior): The exploding behavior for dice that roll the maximum value.
        low_subtracion (bool): If True, subtracts 1 from the number of successes for each dice that rolled a 1.
        dice_modifier (int): The modifier to add to each dice roll.
        pool_modifier (int): The modifier to add to the final result.
        threshold (int): The threshold value to compare the dice rolls to.
    """
    original_dice, extra_dice = roll_pool(number, sides, high_exploding, dice_modifier)
    all_dice = original_dice + extra_dice
    successes = len([dice for dice in all_dice if dice.result+dice_modifier >= threshold])
    if low_subtracion:
        successes -= len([dice for dice in all_dice if dice.result == 1])
    return DicePoolResultSuccesses(
        pool_modifier=pool_modifier,
        dice_results=original_dice,
        extra_dice=extra_dice,
        successes=successes
    )
