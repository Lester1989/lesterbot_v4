import random
from dataclasses import dataclass, field
from enum import IntEnum
from functools import total_ordering
from typing import List


class ExplodingBehavior(IntEnum):
    """Describes the behavior of dice that roll the maximum value. Maybe adding a new dice."""

    NONE = 0
    ONCE = 1
    CASCADING = 2


@dataclass
class DiceResult:
    """Represents the result of a single dice roll."""

    sides: int
    dice_modifier: int
    result: int

    def __eq__(self, __value: object) -> bool:
        return id(self) == id(__value) if isinstance(__value, DiceResult) else NotImplemented

    @property
    def value(self):
        """Returns the value of the dice roll, including any modifiers."""
        return self.dice_modifier + self.result

    @property
    def is_max(self):
        """Returns True if the result is the maximum possible value for the dice."""
        return self.result == self.sides


@dataclass
class DicePoolResult:
    """Represents the result of a pool of dice rolls."""

    pool_modifier: int
    dice_results: list[DiceResult]
    extra_dice: list[DiceResult]
    description: str = ""

    @property
    def all_result(self):
        """Returns all the dice rolls, including any modifiers."""
        return self.dice_results + self.extra_dice


class DicePoolResultSum(DicePoolResult):
    """Represents the result of a pool of dice rolls where the final result is the sum of all the dice rolls."""

    @property
    def sum(self):
        """Returns the sum of all the dice rolls, including any modifiers."""
        return (
            sum(dice.value for dice in self.dice_results)
            + sum(dice.value for dice in self.extra_dice)
            + self.pool_modifier
        )


@dataclass
class DicePoolResultSuccesses(DicePoolResult):
    """Represents the result of a pool of dice rolls where the final result is the number of dice that rolled a value greater than or equal to the threshold."""

    success_threshold: int = -1
    failure_threshold: int = -1

    @property
    def successes(self):
        """Returns the number of dice that rolled a value greater than or equal to the threshold."""
        successes = len([dice for dice in self.all_result if dice.value >= self.success_threshold])
        if self.failure_threshold > 0:
            successes -= len(
                [dice for dice in self.all_result if dice.value <= self.failure_threshold]
            )
        successes += self.pool_modifier
        return successes


@dataclass
@total_ordering
class DicePoolExclusionsSuccesses(DicePoolResultSuccesses):
    """Represents the result of a pool of dice rolls where some dice are excluded from the final result."""

    excluded: list[DiceResult] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, DicePoolExclusionsSuccesses):
            return NotImplemented
        return self.successes == other.successes

    def __lt__(self, other):
        if not isinstance(other, DicePoolExclusionsSuccesses):
            return NotImplemented
        return self.successes < other.successes

    @property
    def successes(self):
        """Returns the number of dice that rolled a value greater than or equal to the threshold."""
        successes = len(
            [
                dice
                for dice in self.all_result
                if dice not in self.excluded and dice.value >= self.success_threshold
            ]
        )
        if self.failure_threshold > 0:
            successes -= len(
                [
                    dice
                    for dice in self.all_result
                    if dice not in self.excluded and dice.value <= self.failure_threshold
                ]
            )
        successes += self.pool_modifier
        return successes

    def formatted(self):
        """Returns the sum of all the dice rolls, including any modifiers."""
        result = ""
        for dice in self.dice_results:
            formatted_dice = format_dice_success_result(
                dice, self.success_threshold, self.failure_threshold
            )
            if dice in self.excluded:
                formatted_dice = f"~~{formatted_dice}~~"
            result += f"{formatted_dice}\n"
        if self.extra_dice:
            result += "Bonuswürfel:\n"
            for dice in self.extra_dice:
                formatted_dice = format_dice_success_result(
                    dice, self.success_threshold, self.failure_threshold
                )
                if dice in self.excluded:
                    formatted_dice = f"~~{formatted_dice}~~"
                result += f"{formatted_dice}\n"
        return result


@dataclass
@total_ordering
class DicePoolExclusionsSum(DicePoolResult):
    """Represents the result of a pool of dice rolls where some dice are excluded from the final result."""

    excluded: list[DiceResult] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, DicePoolExclusionsSum):
            return NotImplemented
        return self.sum == other.sum

    def __lt__(self, other):
        if not isinstance(other, DicePoolExclusionsSum):
            return NotImplemented
        return self.sum < other.sum

    @property
    def sum(self):
        """Returns the sum of all the dice rolls, including any modifiers."""
        return (
            sum(
                dice.value
                for dice in self.dice_results + self.extra_dice
                if dice not in self.excluded
            )
            + self.pool_modifier
        )

    def formatted(self):
        """Returns the sum of all the dice rolls, including any modifiers."""
        result = ""
        for dice in self.dice_results:
            formatted_dice = format_dice_result(dice)
            if dice in self.excluded:
                formatted_dice = f"~~{formatted_dice}~~"
            result += f"{formatted_dice}, "
        if self.extra_dice:
            result += "Bonuswürfel:\n"
            for dice in self.extra_dice:
                formatted_dice = format_dice_result(dice)
                if dice in self.excluded:
                    formatted_dice = f"~~{formatted_dice}~~"
                result += f"{formatted_dice}, "
        return result
    
@dataclass
@total_ordering
class DicePoolExclusionsDifference(DicePoolResult):
    """Represents the result of a pool of dice rolls where some dice are excluded from the final result."""

    threshold: int = 0
    count_below: bool = True
    excluded: list[DiceResult] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, DicePoolExclusionsSum):
            return NotImplemented
        return self.sum == other.sum

    def __lt__(self, other):
        if not isinstance(other, DicePoolExclusionsSum):
            return NotImplemented
        return self.sum < other.sum

    @property
    def sum(self):
        """Returns the sum of all the dice rolls, including any modifiers."""
        return (
            sum(
                min(0,self.threshold-dice.value) if self.count_below else min(0,dice.value-self.threshold)
                for dice in self.dice_results + self.extra_dice
                if dice not in self.excluded
            )
            + self.pool_modifier
        )

    def formatted(self):
        """Returns the sum of all the dice rolls, including any modifiers."""
        result = ""
        for dice in self.dice_results:
            formatted_dice = format_dice_result(dice)
            if dice in self.excluded:
                formatted_dice = f"~~{formatted_dice}~~"
            result += f"{formatted_dice}, "
        if self.extra_dice:
            result += "Bonuswürfel:\n"
            for dice in self.extra_dice:
                formatted_dice = format_dice_result(dice)
                if dice in self.excluded:
                    formatted_dice = f"~~{formatted_dice}~~"
                result += f"{formatted_dice}, "
        return result
    


@dataclass
class ComplexPool:
    number: int = 1
    sides: int = 6
    explode: ExplodingBehavior = ExplodingBehavior.NONE
    explode_threshold: int = -1
    pool_modifier: int = 0
    dice_modifier: int = 0
    success_threshold: int = -1
    failure_threshold: int = -1
    highest_count: int = 0
    lowest_count: int = 0
    count_below: int = -1
    count_above: int = -1
    description: str = ""

    def roll(self):
        if self.failure_threshold > -1 and self.success_threshold == -1:
            self.success_threshold = self.sides // 2 + 1
        base_result = roll_dice_basic(self.number, self.sides, self.dice_modifier)
        extra_result = []
        if self.explode != ExplodingBehavior.NONE:
            exploding_count = len([dice for dice in base_result if dice.is_max])
            extra_result = roll_dice_basic(exploding_count, self.sides, self.dice_modifier)
        if self.explode == ExplodingBehavior.CASCADING:
            new_dice = extra_result.copy()
            extra_result = []
            while new_dice:
                current_dice = new_dice.pop()
                extra_result.append(current_dice)
                if current_dice.is_max:
                    new_dice.append(
                        DiceResult(
                            sides=self.sides,
                            dice_modifier=self.dice_modifier,
                            result=random.randint(1, self.sides),
                        )
                    )
        all_dice = base_result + extra_result
        if self.highest_count > 0:
            all_dice = sorted(all_dice, key=lambda dice: dice.value, reverse=True)[
                : self.highest_count
            ]
        elif self.lowest_count > 0:
            all_dice = sorted(all_dice, key=lambda dice: dice.value)[: self.lowest_count]
        if self.success_threshold > 0 or self.failure_threshold > 0:
            successes = len([dice for dice in all_dice if dice.value >= self.success_threshold])
            if self.failure_threshold > 0:
                successes -= len(
                    [dice for dice in all_dice if dice.value <= self.failure_threshold]
                )
            successes += self.pool_modifier
            return DicePoolExclusionsSuccesses(
                pool_modifier=self.pool_modifier,
                dice_results=base_result,
                extra_dice=extra_result,
                success_threshold=self.success_threshold,
                excluded=[dice for dice in base_result + extra_result if dice not in all_dice],
                description=self.description,
            )
        else:
            successes = None
        if self.count_below > -1 or self.count_above > -1:
            return DicePoolExclusionsDifference(
                pool_modifier=self.pool_modifier,
                dice_results=base_result,
                extra_dice=extra_result,
                excluded=[dice for dice in base_result + extra_result if dice not in all_dice],
                description=self.description,
                threshold=max(self.count_below,self.count_above),
                count_below=self.count_below>-1
            )
        return DicePoolExclusionsSum(
            pool_modifier=self.pool_modifier,
            dice_results=base_result,
            extra_dice=extra_result,
            excluded=[dice for dice in base_result + extra_result if dice not in all_dice],
            description=self.description,
        )


def roll_dice_basic(number: int = 1, sides: int = 6, dice_modifier: int = 0):
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
        DiceResult(sides=sides, dice_modifier=dice_modifier, result=random.randint(1, sides))
        for _ in range(number)
    ]


def roll_dice_sum(
    number: int = 1,
    sides: int = 6,
    high_exploding: ExplodingBehavior = ExplodingBehavior.NONE,
    dice_modifier: int = 0,
    pool_modifier: int = 0,
):
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
        pool_modifier=pool_modifier, dice_results=original_dice, extra_dice=extra_dice
    )


def roll_pool(number: int, sides: int, high_exploding: ExplodingBehavior, dice_modifier: int):
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
        extra_dice = roll_dice_basic(
            number=exploding_count, sides=sides, dice_modifier=dice_modifier
        )
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
    return original_dice, extra_dice


def roll_dice_successes(
    number: int = 1,
    sides: int = 6,
    high_exploding: ExplodingBehavior = ExplodingBehavior.NONE,
    low_subtracion: bool = False,
    dice_modifier: int = 0,
    pool_modifier: int = 0,
    threshold: int = 4,
):
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
    return DicePoolResultSuccesses(
        pool_modifier=pool_modifier,
        dice_results=original_dice,
        extra_dice=extra_dice,
        success_threshold=threshold,
        failure_threshold=1 if low_subtracion else -1,
    )


def format_dice_result(dice_result: DiceResult):
    """
    Formats a DiceResult object as a string.

    Args:
        dice_result (DiceResult): The DiceResult object to format

    Returns:
        A string representing the DiceResult object
    """
    crit_md = "**" if dice_result.is_max else ""
    if dice_result.dice_modifier > 0:
        modifier = f"(+{dice_result.dice_modifier}) -> {crit_md}{dice_result.value}{crit_md}"
    elif dice_result.dice_modifier < 0:
        modifier = f"({dice_result.dice_modifier}) -> {crit_md}{dice_result.value}{crit_md}"
    else:
        modifier = ""
    return f"{crit_md}{dice_result.result}{crit_md} {modifier}"


def format_dice_success_result(dice_result: DiceResult, threshold: int, low_subtracting: int = -1):
    """
    Formats a DiceResult object as a string.

    Args:
        dice_result (DiceResult): The DiceResult object to format
        threshold (int): The threshold value to compare the dice roll to
        low_subtracting (bool): Do we subtract 1 from the number of successes for each dice that rolled a 1?

    Returns:
        A string representing the DiceResult object
    """
    success_md = "**" if dice_result.value >= threshold else ""
    if low_subtracting and dice_result.value <= low_subtracting:
        success_md = "~~"
    if dice_result.dice_modifier > 0:
        modifier = f"(+{dice_result.dice_modifier}) -> {success_md}{dice_result.value}{success_md}"
    elif dice_result.dice_modifier < 0:
        modifier = f"({dice_result.dice_modifier}) -> {success_md}{dice_result.value}{success_md}"
    else:
        modifier = ""
    return f"{success_md}{dice_result.result}{success_md} {modifier}"
