from interactions import (
    Embed,
    Extension,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    slash_command,
    slash_option,
)

from app.library.complex_dice_parser import Parser, ParsingState
from app.library.polydice import (
    DicePoolExclusionsSuccesses,
    DicePoolExclusionsSum,
    DiceResult,
    ExplodingBehavior,
    format_dice_result,
    format_dice_success_result,
    roll_dice_successes,
    roll_dice_sum,
)


class RollComplex(Extension):
    async def async_start(self):
        print("Starting RollComplex Extension")

    @slash_command(name="roll_help", description="Displays help for the /roll_complex command")
    async def roll_help(self, ctx: SlashContext):
        await ctx.send(
            """
**/roll_complex help**
You can use the following Syntax to roll dice:
* Space seperates the dices Descriptions
* Each Description can start with number, if none is given 1 is assumed
* Normal Dice Types are defined by a letter(w  / W / d / D) followed by the number of sides on the dice, if none is given 6 is assumed
* after the number of sides you can be more special dice behaviors:
s for success (greater or equal)
f for failure (less or equal)
! for single exploding dice (greater or equal)
!! for recursively exploding dice (greater or equal)
h to use only the highest values (amount)
b to use only the lowest values (amount)
+/- to add a modifier to the dice pool (success count if s is used, sum if not)
++/-- to add a modifier to each dice result

Each description can be followed by a comment indicated by a #, the comment will be displayed in the result

**Examples:**
```/roll_complex 2d6```
Rolls two 6-sided dice
```/roll_complex 2d6 1d10```
Rolls two 6-sided dice and one 10-sided dice
```/roll_complex 4d6h2 #Attack```
Rolls four 6-sided dice and uses the two highest values. Says "Attack" in the result
```/roll_complex 4d10s6f1!10 #Jump```
Rolls four 10-sided dice and counts the number of dice that rolled a 6 or higher, subtracts the number of dice that rolled a 1, and explodes any dice that rolled a 10. Says "Jump" in the result
"""
        )

    @slash_command(
        name="roll_complex",
        description="Rolls a number of dice and displays the result see /roll_help for more info",
    )
    @slash_option(
        name="dice_pool", description="The dice to roll", required=True, opt_type=OptionType.STRING
    )
    async def roll_complex(self, ctx: SlashContext, dice_pool: str):
        await ctx.defer()

        dice_description = dice_pool.split("#")[0].split(" ")
        print(dice_description)
        comment = dice_pool.split("#")[1] if "#" in dice_pool else ""
        dice_results = [
            Parser(description.strip()).build_pool().roll()
            for description in dice_description
            if description.strip()
        ]
        total_successes = sum(
            result.successes
            for result in dice_results
            if isinstance(result, DicePoolExclusionsSuccesses)
        )
        total_sum = sum(
            result.sum for result in dice_results if isinstance(result, DicePoolExclusionsSum)
        )
        embed = Embed(
            title=f"Rolling for {ctx.author.display_name.split(' ')[0]}",
            description=f"Rolling {dice_pool}\nTotal Successes: {total_successes}\nTotal Sum: {total_sum}",
            footer=f"{comment}",
        )
        for result in dice_results:
            embed.add_field(name=f"{result.description}:", value=result.formatted())
            if len(embed.fields) > 24:
                await ctx.send(embed=embed)
                embed = Embed(
                    title=f"Rolling for {ctx.author.display_name.split(' ')[0]} (continued)",
                    description=f"Rolling {dice_pool}\nTotal Successes: {total_successes}\nTotal Sum: {total_sum}",
                    footer=f"{comment}",
                )
        await ctx.send(embed=embed)
