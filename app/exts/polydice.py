from interactions import (
    Embed,
    Extension,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    slash_command,
    slash_option,
)

from app.library.polydice import (
    DiceResult,
    ExplodingBehavior,
    format_dice_result,
    format_dice_success_result,
    roll_dice_successes,
    roll_dice_sum,
)


class PolyDice(Extension):
    async def async_start(self):
        print("Starting PolyDice Extension")

    @slash_command(
        name="roll_successes",
        description="Rolls a number of dice and counts the number of successes",
    )
    @slash_option(
        name="number",
        description="The number of dice to roll (default 1)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="sides",
        description="The number of sides on each dice (default 6)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="high_exploding",
        description="The exploding behavior for dice that roll the maximum value (default None)",
        required=False,
        opt_type=OptionType.INTEGER,
        choices=[
            SlashCommandChoice(name="None", value=ExplodingBehavior.NONE),
            SlashCommandChoice(name="Once", value=ExplodingBehavior.ONCE),
            SlashCommandChoice(name="Forever", value=ExplodingBehavior.CASCADING),
        ],
    )
    @slash_option(
        name="low_subtracting",
        description="Do we subtract 1 from the number of successes for each dice that rolled a 1? (default False)",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="dice_modifier",
        description="The modifier to add to each dice roll (default 0)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="pool_modifier",
        description="The modifier to add to the final number of successes (default 0)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="threshold",
        description="The threshold value to compare the dice rolls to (default 4)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    async def roll_successes(
        self,
        ctx: SlashContext,
        number: int = 1,
        sides: int = 6,
        high_exploding: ExplodingBehavior = ExplodingBehavior.NONE,
        low_subtracting: bool = False,
        dice_modifier: int = 0,
        pool_modifier: int = 0,
        threshold: int = 4,
    ):
        """Rolls a number of dice and counts the number of successes."""
        result = roll_dice_successes(
            number, sides, high_exploding, low_subtracting, dice_modifier, pool_modifier, threshold
        )
        color = 0xFFFFFF
        if result.successes < 0:
            color = 0xFF0000
        elif result.successes == 0:
            color = 0x000000
        elif result.successes < 3:
            color = 0x00AA00
        else:
            color = 0x00FF00
        embed = Embed(
            title="Roll Successes",
            description=f'{result.successes} Erfolge{" (Fehlschlag)" if result.successes <= 0 else ""}',
            color=color,
        )
        embed.add_field(name="Würfelpool:", value=f"{number}W{sides}")
        embed.add_field(
            name="Ergebnis:",
            value=", ".join(
                [
                    format_dice_success_result(dice, threshold, low_subtracting)
                    for dice in result.dice_results
                ]
            ),
        )
        if high_exploding != ExplodingBehavior.NONE and result.extra_dice:
            embed.add_field(
                name="Bonuswürfel:",
                value=", ".join(
                    [
                        format_dice_success_result(dice, threshold, low_subtracting)
                        for dice in result.extra_dice
                    ]
                ),
            )
        if pool_modifier != 0:
            embed.add_field(name="Gekaufte Erfolge:", value=str(pool_modifier))
        await ctx.send(embed=embed)

    @slash_command(
        name="roll_sum", description="Rolls a number of dice and returns the sum of the results"
    )
    @slash_option(
        name="number",
        description="The number of dice to roll (default 1)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="sides",
        description="The number of sides on each dice (default 6)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="high_exploding",
        description="The exploding behavior for dice that roll the maximum value (default None)",
        required=False,
        opt_type=OptionType.INTEGER,
        choices=[
            SlashCommandChoice(name="None", value=ExplodingBehavior.NONE),
            SlashCommandChoice(name="Once", value=ExplodingBehavior.ONCE),
            SlashCommandChoice(name="Forever", value=ExplodingBehavior.CASCADING),
        ],
    )
    @slash_option(
        name="dice_modifier",
        description="The modifier to add to each dice roll (default 0)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="pool_modifier",
        description="The modifier to add to the final result (default 0)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    async def roll_sum(
        self,
        ctx: SlashContext,
        number: int = 1,
        sides: int = 6,
        high_exploding: ExplodingBehavior = ExplodingBehavior.NONE,
        dice_modifier: int = 0,
        pool_modifier: int = 0,
    ):
        """Rolls a number of dice and returns the sum of the results."""
        result = roll_dice_sum(number, sides, high_exploding, dice_modifier, pool_modifier)
        color = 0xFFFFFF
        if result.sum == number:
            color = 0xFF0000
        elif result.sum == number * sides // 2:
            color = 0x000000
        elif result.sum < number * (sides // 2 + 1):
            color = 0x00AA00
        else:
            color = 0x00FF00
        embed = Embed(
            title="Roll Sum",
            description=f'{result.sum}{" (Fehlschlag)" if result.sum <= 0 else ""}',
            color=color,
        )
        embed.add_field(name="Würfelpool:", value=f"{number}W{sides}")
        embed.add_field(
            name="Ergebnis:",
            value=", ".join([format_dice_result(dice) for dice in result.dice_results]),
        )
        if high_exploding != ExplodingBehavior.NONE and result.extra_dice:
            embed.add_field(
                name="Bonuswürfel:",
                value=", ".join([format_dice_result(dice) for dice in result.extra_dice]),
            )
        if pool_modifier != 0:
            embed.add_field(name="Bonuswert:", value=str(pool_modifier))
        await ctx.send(embed=embed)
