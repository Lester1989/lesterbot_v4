"""This module contains the RollComplex Extension."""
from interactions import (
    AutocompleteContext,
    Button,
    ButtonStyle,
    ComponentContext,
    Embed,
    Extension,
    LocalisedDesc,
    LocalisedName,
    Modal,
    ModalContext,
    OptionType,
    ShortText,
    SlashCommandChoice,
    SlashContext,
    component_callback,
    modal_callback,
    slash_command,
    slash_option,
    spread_to_rows,
)

import app.localizer as localizer
from app.library.complex_dice_parser import Parser
from app.library.polydice import (
    DicePoolExclusionsDifference,
    DicePoolExclusionsSuccesses,
    DicePoolExclusionsSum,
)
from app.library.saved_rolls import (
    SavedRoll,
    Session,
    engine,
    get_by_id,
    get_by_user,
    invalidate_cache,
)


class RollComplex(Extension):
    """An extension for rolling complex dice pools."""
    async def async_start(self):
        """Print a message when the extension is started."""
        print("Starting RollComplex Extension")

    @slash_command(
        name="roll_help",
        description=LocalisedDesc(**localizer.translations("roll_help_description")),
    )
    async def roll_help(self, ctx: SlashContext):
        """Send a help message for the complex dice rolling command."""
        await ctx.send( # TODO: LOCALIZATION FLAG
            """
**/roll_complex help**
You can use the following Syntax to roll dice:
* Space seperates the dices Descriptions
* Each Description can start with number, if none is given 1 is assumed
* Normal Dice Types are defined by a letter(w  / W / d / D) followed by the number of sides on the dice, if none is given 6 is assumed
* after the number of sides you can be more special dice behaviors:
s for success (greater or equal)
f for failure (less or equal)
< counts amount below
> counts amount above
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

```/roll_complex d20<14 d20<12 d20<13 #Mu Ch Kl```
Rolls three 20-sided dice and counts the value if it is below 14 / 12 / 13. Says "Mu Ch Kl" in the result.
"""
        )

    @slash_command(
        name="roll_complex",
        description=LocalisedDesc(**localizer.translations("roll_complex_description")),
    )
    @slash_option(
        name="dice_pool",
        description=LocalisedDesc(**localizer.translations("dice_pool_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    async def roll_complex(self, ctx: SlashContext, dice_pool: str):
        """Roll a complex dice pool."""
        await ctx.defer()
        result_embeds = self.create_embeds(ctx, ctx.author.display_name.split(" ")[0], dice_pool)
        action_rows = spread_to_rows(
            Button(style=ButtonStyle.GRAY, label=".", custom_id=dice_pool, disabled=True),
            Button(
                style=ButtonStyle.BLUE,
                label=localizer.translate(ctx.locale, "save"),
                custom_id="save_complex_pool",
            ),
        )
        for embed in result_embeds:
            await ctx.send(f'{ctx.author.mention} {localizer.translate(ctx.locale,"rolled")}',embed=embed, components=action_rows)

    @slash_command(
        name="save_roll",
        description=LocalisedDesc(**localizer.translations("save_roll_description")),
    )
    @slash_option(
        name="dice_pool",
        description=LocalisedDesc(**localizer.translations("dice_pool_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="roll_name",
        description=LocalisedDesc(**localizer.translations("roll_name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="scope",
        description=LocalisedDesc(
            **localizer.translations(
                "should_the_roll_be_available_serverwide_categorywide_or_just_in_this_channeldefault"
            )
        ),
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("serverwide")), value="server"
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("categorywide")), value="category"
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("channelwide")), value="channel"
            ),
        ],
    )
    async def save_roll(
        self, ctx: SlashContext, dice_pool: str, roll_name: str, scope: str = "channel"
    ):
        """Save a complex dice pool."""
        await self.save_roll_to_db(ctx, roll_name, dice_pool, scope)
        await ctx.send(localizer.translate(ctx.locale, "saved"), ephemeral=True)

    @slash_command(
        name="my_rolls",
        description=LocalisedDesc(**localizer.translations("my_rolls_description")),
    )
    async def my_rolls(self, ctx: SlashContext):
        """List all saved rolls for the user."""
        saved_rolls = get_by_user(str(ctx.author_id))
        if not saved_rolls:
            await ctx.send(localizer.translate(ctx.locale, "no_saved_rolls"))
            return
        embed = Embed(title=localizer.translate(ctx.locale, "your_saved_rolls"))
        for saved_roll in saved_rolls:
            embed.add_field(
                name=f"{saved_roll.name} ({saved_roll.scope})",
                value=f"{saved_roll.dice_pool}",
            )
        await ctx.send(embed=embed)

    @slash_command(
        name="named_roll",
        description=LocalisedDesc(**localizer.translations("named_roll_description")),
    )
    @slash_option(
        name="roll_name",
        description=LocalisedDesc(**localizer.translations("roll_name_description")),
        opt_type=OptionType.STRING,
        required=True,
        autocomplete=True,
    )
    async def named_roll(self, ctx: SlashContext, roll_name: str):
        """Roll a saved dice pool."""
        saved_roll_id = int(roll_name)
        saved_roll = get_by_id(saved_roll_id)

        await ctx.defer()
        result_embeds = self.create_embeds(
            ctx, ctx.author.display_name.split(" ")[0], saved_roll.dice_pool
        )
        for embed in result_embeds:
            await ctx.send(embed=embed)

    @named_roll.autocomplete("roll_name")
    async def roll_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocomplete the name of a saved roll."""
        string_option_input = ctx.input_text

        result = [
            {"name": saved_roll.name, "value": str(saved_roll.id)}
            for saved_roll in get_by_user(str(ctx.author_id))
            if string_option_input.lower() in saved_roll.name.lower()
            and saved_roll.is_available(
                str(ctx.guild_id), str(ctx.channel.parent_id), str(ctx.channel_id)
            )
        ][:10]
        await ctx.send(choices=result)

    def create_embeds(self, ctx: SlashContext, display_name: str, dice_pool: str):
        """Create the embeds for the dice pool."""
        result_embeds = []
        dice_description = dice_pool.split("#")[0].split(" ")
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
            result.sum * (-1 if isinstance(result, DicePoolExclusionsDifference) else 1)
            for result in dice_results
            if isinstance(result, (DicePoolExclusionsSum, DicePoolExclusionsDifference))
        )
        embed = Embed(
            title=localizer.translate(
                ctx.locale, "rolling_for_display_name", display_name=display_name
            ),
            description=localizer.translate(
                ctx.locale,
                "rolling_dice_poolntotal_successes_total_successesntotal_sum_total_sum",
                dice_pool=dice_pool,
                total_successes=total_successes,
                total_sum=total_sum,
            ),
            footer=f"{comment}",
        )
        for result in dice_results:
            embed.add_field(name=f"{result.description}:", value=result.formatted())
            if len(embed.fields) > 24:
                result_embeds.append(embed)
                embed = Embed(
                    title=localizer.translate(
                        ctx.locale, "rolling_for_display_name_continued", display_name=display_name
                    ),
                    description=localizer.translate(
                        ctx.locale,
                        "rolling_dice_poolntotal_successes_total_successesntotal_sum_total_sum",
                        dice_pool=dice_pool,
                        total_successes=total_successes,
                        total_sum=total_sum,
                    ),
                    footer=f"{comment}",
                )
        if len(embed.fields) > 0:
            result_embeds.append(embed)
        return result_embeds

    @component_callback("save_complex_pool")
    async def button_save_complex_pool(self, ctx: ComponentContext):
        """Handle the button press to save a complex dice pool."""
        save_modal = Modal(
            ShortText(label=localizer.translate(ctx.locale, "name"), custom_id="roll_name"),
            ShortText(
                label=localizer.translate(ctx.locale, "definition"),
                custom_id="dice_pool",
                value=ctx.message.components[0].components[0].custom_id,
            ),
            ShortText(
                label=localizer.translate(ctx.locale, "scope_servercategory_or_channel"),
                custom_id="scope",
                value="channel",
            ),
            title=localizer.translate(ctx.locale, "save_this_roll"),
            custom_id="save_complex_roll",
        )
        await ctx.send_modal(modal=save_modal)

    @modal_callback("save_complex_roll")
    async def on_modal_answer(self, ctx: ModalContext, roll_name: str, dice_pool: str, scope: str):
        """Save a complex dice pool."""
        await self.save_roll_to_db(ctx, roll_name, dice_pool, scope)
        await ctx.send(
            localizer.translate(ctx.locale, "saved"),
            ephemeral=True,
        )

    

    async def save_roll_to_db(self, ctx: SlashContext, roll_name: str, dice_pool: str, scope: str):
        if scope == "server":
            discord_id = str(ctx.guild_id)
        elif scope == "category":
            discord_id = str(ctx.channel.parent_id)
        else:
            discord_id = str(ctx.channel_id)
        db_object = SavedRoll(
            user_id=str(ctx.author_id),
            discord_id=discord_id,
            scope=scope,
            dice_pool=dice_pool,
            name=roll_name,
        )
        print('saving roll',db_object)
        with Session(
            engine,
        ) as session:
            session.add(db_object)
            session.commit()
        invalidate_cache()
