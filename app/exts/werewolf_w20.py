from config import SCOPE_KWARG
from interactions import Attachment, Embed, Extension, slash_command, slash_option, SlashContext, OptionType, AutocompleteContext
from library.polydice import roll_dice_successes,  ExplodingBehavior,  format_dice_success_result
from library.werewolf_gifts import Gift,parse_json,load_gifts
import aiohttp

class WerewolfW20(Extension):

    gifts:list[Gift] = []
    gift_names:list[str] = []

    async def async_start(self):
        self.gifts = load_gifts()
        self.gift_names = [ gift.name.lower() for gift in self.gifts ]
        print("Starting Werewolf Extension")

    @slash_command(
            name="ww",
            description="Rolls a number of dice for Werwolf 20th edition")
    @slash_option(
            name="number",
            description="The number of dice to roll (default 1)",
            required=False,
            opt_type=OptionType.INTEGER)
    @slash_option(
            name="difficulty",
            description="The difficulty of the roll (default 6)",
            required=False,
            opt_type=OptionType.INTEGER)
    @slash_option(
            name="ones_cancel",
            description="Do we cancel ones? (default True)",
            required=False,
            opt_type=OptionType.BOOLEAN)
    @slash_option(
            name="specialty",
            description="Do we add specialty dice? (default False)",
            required=False,
            opt_type=OptionType.BOOLEAN)
    @slash_option(
            name="spent_willpower",
            description="Do we add Success for Willpower? (default False)",
            required=False,
            opt_type=OptionType.BOOLEAN)
    async def ww(self, ctx: SlashContext,number: int = 1, difficulty: int = 6, ones_cancel: bool = True, specialty: bool = False, spent_willpower: bool = False):
        """
        Rolls a number of dice and counts the number of successes
        """
        result = roll_dice_successes(number, 10, ExplodingBehavior.ONCE if specialty else ExplodingBehavior.NONE, ones_cancel, 0, 1 if spent_willpower else 0, difficulty)
        color = 0xFFFFFF
        if result.successes < 0:
            color = 0xFF0000
        elif result.successes > 0:
            color = 0x00FF00
        else:
            color = 0x0000FF
        embed = Embed(
            title=f"Rolling {number} dice with difficulty {difficulty}",
            color=color,
        )
        embed.add_field(
            name="Dice Results",
            value="\n".join([format_dice_success_result(dice_result, difficulty, ones_cancel) for dice_result in result.dice_results+result.extra_dice]),
            inline=False
        )
        embed.add_field(
            name="Successes",
            value=f"{result.successes} + {result.pool_modifier}",
            inline=False
        )
        await ctx.send(embed=embed)

    @slash_command(
        name="show_gift",
        description="Show gift description")
    @slash_option(
        name="gift_name",
        description="The name of the gift",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True)
    async def show_gift(self, ctx: SlashContext, gift_name: str):
        """
        Show gift description
        """
        gift = next((gift for gift in self.gifts if gift.name == gift_name), None)
        embed = Embed(
            title=gift.name,
            description=gift.description_fluff,
            color=0xFFFFFF
        )
        embed.add_field(
            name="System",
            value=gift.description_system,
            inline=False
        )
        embed.add_field(
            name="Available for",
            value=gift.available_for,
            inline=False
        )
        await ctx.send(embed=embed)

    @show_gift.autocomplete("gift_name")
    async def gift_name_autocomplete(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text
        print(f"Autocomplete for {string_option_input}")
        print(f"Gift names: {self.gift_names}")

        result = [{"name":gift_name,"value":gift_name} for gift_name in self.gift_names if string_option_input.lower() in  gift_name][:10]
        print(f"Result: {result}")
        await ctx.send(choices=result)

    @slash_command(
        name="upload_gifts",
        description="Upload gifts from a CSV file",
        **SCOPE_KWARG)
    @slash_option(
        name="file",
        description="The CSV file to upload",
        required=True,
        opt_type=OptionType.ATTACHMENT)
    async def upload_gifts(self, ctx: SlashContext, file:Attachment):
        """
        Upload gifts from a CSV file
        """
        content = await self.download_file(file.url, file.filename)
        self.gifts = parse_json(content)
        self.gift_names = [ gift.name.lower() for gift in self.gifts ]
        await ctx.send(f"Uploaded {len(self.gifts)} gifts")


    async def download_file(self, url: str, file_path: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
        with open(file_path, 'r', encoding='utf8') as f:
            return f.read()
