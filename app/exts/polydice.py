"""
This module contains the PolyDice extension for the bot.

The PolyDice extension provides commands for rolling dice and counting successes.
"""
from interactions import (
    Embed,
    Extension,
    LocalisedDesc,
    LocalisedName,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    slash_command,
    slash_option,
)

import app.localizer as localizer
from app.library.polydice import (
    ExplodingBehavior,
    format_dice_result,
    format_dice_success_result,
    roll_dice_successes,
    roll_dice_sum,
)


class PolyDice(Extension):
    """An extension for rolling dice and counting successes."""
    async def async_start(self):
        """Print a message when the extension is started."""
        print("Starting PolyDice Extension")

    @slash_command(
        name="roll_successes",
        description=LocalisedDesc(**localizer.translations("roll_successes_description")),
    )
    @slash_option(
        name="number",
        description=LocalisedDesc(**localizer.translations("number_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="sides",
        description=LocalisedDesc(**localizer.translations("sides_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="high_exploding",
        description=LocalisedDesc(
            **localizer.translations(
                "the_exploding_behavior_for_dice_that_roll_the_maximum_value_default_none"
            )
        ),
        required=False,
        opt_type=OptionType.INTEGER,
        choices=[
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("none")), value=ExplodingBehavior.NONE
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("once")), value=ExplodingBehavior.ONCE
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("forever")),
                value=ExplodingBehavior.CASCADING,
            ),
        ],
    )
    @slash_option(
        name="low_subtracting",
        description=LocalisedDesc(**localizer.translations("low_subtracting_description")),
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="dice_modifier",
        description=LocalisedDesc(**localizer.translations("dice_modifier_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="pool_modifier",
        description=LocalisedDesc(**localizer.translations("pool_modifier_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="threshold",
        description=LocalisedDesc(**localizer.translations("threshold_description")),
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
            title=localizer.translate(ctx.locale, "roll_successes"),
            description=localizer.translate(
                ctx.locale,
                "resultsuccesses_erfolge_fehlschlag_if_resultsuccesses__0_else_",
                resultsuccesses=result.successes,
                _fehlschlag_if_resultsuccesses__0_else_=localizer.translate(
                    ctx.locale, "_fehlschlag"
                )
                if result.successes <= 0
                else "",
            ),
            color=color,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "würfelpool"),
            value=localizer.translate(ctx.locale, "numberwsides", number=number, sides=sides),
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "ergebnis"),
            value=", ".join(
                [
                    format_dice_success_result(dice, threshold, low_subtracting)
                    for dice in result.dice_results
                ]
            ),
        )
        if high_exploding != ExplodingBehavior.NONE and result.extra_dice:
            embed.add_field(
                name=localizer.translate(ctx.locale, "bonuswürfel"),
                value=", ".join(
                    [
                        format_dice_success_result(dice, threshold, low_subtracting)
                        for dice in result.extra_dice
                    ]
                ),
            )
        if pool_modifier != 0:
            embed.add_field(
                name=localizer.translate(ctx.locale, "gekaufte_erfolge"), value=str(pool_modifier)
            )
        await ctx.send(f'{ctx.author.mention} {localizer.translate(ctx.locale,"rolled")}',embed=embed)

    @slash_command(
        name="roll_sum", description=LocalisedDesc(**localizer.translations("roll_sum_description"))
    )
    @slash_option(
        name="number",
        description=LocalisedDesc(**localizer.translations("number_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="sides",
        description=LocalisedDesc(**localizer.translations("sides_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="high_exploding",
        description=LocalisedDesc(
            **localizer.translations(
                "the_exploding_behavior_for_dice_that_roll_the_maximum_value_default_none"
            )
        ),
        required=False,
        opt_type=OptionType.INTEGER,
        choices=[
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("none")), value=ExplodingBehavior.NONE
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("once")), value=ExplodingBehavior.ONCE
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("forever")),
                value=ExplodingBehavior.CASCADING,
            ),
        ],
    )
    @slash_option(
        name="dice_modifier",
        description=LocalisedDesc(**localizer.translations("dice_modifier_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="pool_modifier",
        description=LocalisedDesc(**localizer.translations("pool_modifier_description")),
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
            title=localizer.translate(ctx.locale, "roll_sum"),
            description=f'{result.sum}{LocalisedDesc(**localizer.translations("_fehlschlag")) if result.sum <= 0 else ""}',
            color=color,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "würfelpool"),
            value=localizer.translate(ctx.locale, "numberwsides", number=number, sides=sides),
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "ergebnis"),
            value=", ".join([format_dice_result(dice) for dice in result.dice_results]),
        )
        if high_exploding != ExplodingBehavior.NONE and result.extra_dice:
            embed.add_field(
                name=localizer.translate(ctx.locale, "bonuswürfel"),
                value=", ".join([format_dice_result(dice) for dice in result.extra_dice]),
            )
        if pool_modifier != 0:
            embed.add_field(
                name=localizer.translate(ctx.locale, "bonuswert"), value=str(pool_modifier)
            )
        await ctx.send(f'{ctx.author.mention} {localizer.translate(ctx.locale,"rolled")}',embed=embed)
