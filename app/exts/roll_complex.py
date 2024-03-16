from interactions import (
    AutocompleteContext,
    Button,
    ButtonStyle,
    ComponentContext,
    Embed,
    Extension,
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

from app.library.complex_dice_parser import Parser, ParsingState
from app.library.polydice import (
    DicePoolExclusionsSuccesses,
    DicePoolExclusionsSum,
    DicePoolExclusionsDifference,
    DiceResult,
    ExplodingBehavior,
    format_dice_result,
    format_dice_success_result,
    roll_dice_successes,
    roll_dice_sum,
)
from app.library.saved_rolls import SavedRoll,engine,Session,get_by_id,get_by_user,invalidate_cache


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
        description="Rolls a number of dice and displays the result see /roll_help for more info",
    )
    @slash_option(
        name="dice_pool", description="The dice to roll", required=True, opt_type=OptionType.STRING
    )
    async def roll_complex(self, ctx: SlashContext, dice_pool: str):
        await ctx.defer()
        result_embeds = self.create_embeds(ctx.author.display_name.split(' ')[0],dice_pool)
        action_rows = spread_to_rows(
            Button(style=ButtonStyle.GRAY,label=".",custom_id=dice_pool,disabled=True),
            Button(style=ButtonStyle.BLUE,label="Save",custom_id='save_complex_pool')
        )
        for embed in result_embeds:
            await ctx.send(embed=embed,components=action_rows)

    @slash_command(
        name="save_roll",
        description="Saves a complex roll with a name for you"
    )
    @slash_option(
        name="dice_pool", description="The dice to roll", required=True, opt_type=OptionType.STRING
    )
    @slash_option(
        name="roll_name", description="a name you would give to this roll", required=True, opt_type=OptionType.STRING
    )
    @slash_option(
        name="scope", 
        description="should the roll be available server-wide, category-wide or just in this channel(default)", 
        required=False, 
        opt_type=OptionType.STRING, 
        choices=[
            SlashCommandChoice(name='serverwide',value='server'),
            SlashCommandChoice(name='categorywide',value='category'),
            SlashCommandChoice(name='channelwide',value='channel'),
        ]
    )
    async def save_roll(self, ctx:SlashContext, dice_pool:str,roll_name:str,scope:str="channel"):
        if scope == 'server':
            discord_id = str(ctx.guild_id)
        elif scope == 'category':
            discord_id = str(ctx.channel.parent_id)
        else:
            discord_id = str(ctx.channel_id)
        db_object = SavedRoll(user_id=str(ctx.author_id),discord_id=discord_id,scope=scope,dice_pool=dice_pool,name=roll_name)
        with Session(engine,) as session:
            session.add(db_object)
            session.commit()
        invalidate_cache()
        await ctx.send("saved",ephemeral=True)

    @slash_command(
        name='named_roll',
        description='reuses a roll previosly saved by you'
    )
    @slash_option(
        name='roll_name',description='name of the roll specified on save', opt_type=OptionType.STRING,required=True,autocomplete=True
    )
    async def named_roll(self,ctx:SlashContext,roll_name:str):
        saved_roll_id = int(roll_name)
        saved_roll = get_by_id(saved_roll_id)
        
        await ctx.defer()
        result_embeds = self.create_embeds(ctx.author.display_name.split(' ')[0],saved_roll.dice_pool)
        for embed in result_embeds:
            await ctx.send(embed=embed)

    @named_roll.autocomplete('roll_name')
    async def roll_name_autocomplete(self,ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        
        result = [
            {"name": saved_roll.name, "value": str(saved_roll.id)}
            for saved_roll in get_by_user(str(ctx.author_id))
            if string_option_input.lower() in saved_roll.name and saved_roll.is_available(str(ctx.guild_id),str(ctx.channel.parent_id),str(ctx.channel_id))
        ][:10]
        await ctx.send(choices=result)


    def create_embeds(self,display_name:str,dice_pool:str):
        result_embeds = []
        dice_description = dice_pool.split("#")[0].split(" ")
        print(dice_description)
        comment = dice_pool.split("#")[1] if "#" in dice_pool else ""
        dice_results = [
            Parser(description.strip()).build_pool().roll()
            for description in dice_description
            if description.strip()
        ]
        for dr in dice_results:
            print(type(dr), dr.description,dr.formatted())
        total_successes = sum(
            result.successes
            for result in dice_results
            if isinstance(result, DicePoolExclusionsSuccesses)
        )
        total_sum = sum(
            result.sum * (-1 if isinstance(result, DicePoolExclusionsDifference) else 1)
            for result in dice_results
            if isinstance( result, (DicePoolExclusionsSum, DicePoolExclusionsDifference) )
        )
        embed = Embed(
            title=f"Rolling for {display_name}",
            description=f"Rolling {dice_pool}\nTotal Successes: {total_successes}\nTotal Sum: {total_sum}",
            footer=f"{comment}",
        )
        for result in dice_results:
            embed.add_field(name=f"{result.description}:", value=result.formatted())
            if len(embed.fields) > 24:
                result_embeds.append(embed)
                embed = Embed(
                    title=f"Rolling for {display_name} (continued)",
                    description=f"Rolling {dice_pool}\nTotal Successes: {total_successes}\nTotal Sum: {total_sum}",
                    footer=f"{comment}",
                )
        if len(embed.fields) > 0:
            result_embeds.append(embed)
        print(f'constructed {len(result_embeds)} embeds')
        return result_embeds

    @component_callback("save_complex_pool")
    async def button_save_complex_pool(self,ctx: ComponentContext):
        save_modal = Modal(
            ShortText(label="Name", custom_id="roll_name"),
            ShortText(label="Definition", custom_id="dice_pool",value=ctx.message.components[0].components[0].custom_id),
            ShortText(label="Scope (server,category or channel)", custom_id="scope",value='channel'),
            title="Save this Roll",
            custom_id="save_complex_roll",
        )
        await ctx.send_modal(modal=save_modal)

    @modal_callback("save_complex_roll")
    async def on_modal_answer(self,ctx: ModalContext, roll_name: str, dice_pool: str,scope:str):
        if scope == 'server':
            discord_id = str(ctx.guild_id)
        elif scope == 'category':
            discord_id = str(ctx.channel.parent_id)
        else:
            discord_id = str(ctx.channel_id)
        db_object = SavedRoll(user_id=str(ctx.author_id),discord_id=discord_id,scope=scope,dice_pool=dice_pool,name=roll_name)
        with Session(engine,) as session:
            session.add(db_object)
            session.commit()
        invalidate_cache()
        await ctx.send("saved",ephemeral=True)

