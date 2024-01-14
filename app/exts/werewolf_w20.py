import re

import aiohttp
from interactions import (
    Attachment,
    AutocompleteContext,
    Button,
    ButtonStyle,
    ComponentContext,
    Embed,
    Extension,
    OptionType,
    SlashContext,
    component_callback,
    slash_command,
    slash_option,
    spread_to_rows,
)

from app.library.polydice import (
    ExplodingBehavior,
    format_dice_success_result,
    roll_dice_successes,
)
from app.library.werewolf_gifts import Gift, load_gifts, parse_json

regex_pattern = re.compile(r"show_gift_(.*)")


class WerewolfW20(Extension):
    gifts: list[Gift] = []
    gift_names: list[str] = []

    async def async_start(self):
        self.gifts = load_gifts()
        self.gift_names = [gift.name.lower() for gift in self.gifts]
        print("Starting Werewolf Extension")

    @slash_command(name="ww", description="Rolls a number of dice for Werwolf 20th edition")
    @slash_option(
        name="number",
        description="The number of dice to roll (default 1)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="difficulty",
        description="The difficulty of the roll (default 6)",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="ones_cancel",
        description="Do we cancel ones? (default True)",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="specialty",
        description="Do we add specialty dice? (default False)",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="spent_willpower",
        description="Do we add Success for Willpower? (default False)",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    async def ww(
        self,
        ctx: SlashContext,
        number: int = 1,
        difficulty: int = 6,
        ones_cancel: bool = True,
        specialty: bool = False,
        spent_willpower: bool = False,
    ):
        """Rolls a number of dice and counts the number of successes."""
        result = roll_dice_successes(
            number,
            10,
            ExplodingBehavior.ONCE if specialty else ExplodingBehavior.NONE,
            ones_cancel,
            0,
            1 if spent_willpower else 0,
            difficulty,
        )
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
            value="\n".join(
                [
                    format_dice_success_result(dice_result, difficulty, ones_cancel)
                    for dice_result in result.dice_results + result.extra_dice
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Successes", value=f"{result.successes} + {result.pool_modifier}", inline=False
        )
        await ctx.send(embed=embed)

    @slash_command(name="show_gift", description="Show gift description")
    @slash_option(
        name="gift_name",
        description="The name of the gift",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True,
    )
    async def show_gift(self, ctx: SlashContext, gift_name: str):
        """Show gift description."""
        return await self.display_gift(ctx, gift_name)

    async def display_gift(self, ctx: SlashContext, gift_name: str):
        gift = next((gift for gift in self.gifts if gift.name.lower() == gift_name.lower()), None)
        if gift is None:
            await ctx.send(f"Could not find gift {gift_name}")
            return
        embed = Embed(title=gift.name, description=gift.description_fluff, color=0xFFFFFF)
        embed.add_field(name="System", value=gift.description_system, inline=False)
        embed.add_field(name="Available for", value=gift.available_for, inline=False)
        await ctx.send(embed=embed)

    @show_gift.autocomplete("gift_name")
    async def gift_name_autocomplete(self, ctx: AutocompleteContext):
        string_option_input = ctx.input_text

        result = [
            {"name": gift_name, "value": gift_name}
            for gift_name in self.gift_names
            if string_option_input.lower() in gift_name
        ][:10]
        await ctx.send(choices=result)

    @slash_command(name="upload_gifts", description="Upload gifts from a CSV file")
    @slash_option(
        name="file",
        description="The CSV file to upload",
        required=True,
        opt_type=OptionType.ATTACHMENT,
    )
    async def upload_gifts(self, ctx: SlashContext, file: Attachment):
        """Upload gifts from a CSV file."""
        content = await self.download_file(file.url, file.filename)
        self.gifts = parse_json(content)
        self.gift_names = [gift.name.lower() for gift in self.gifts]
        await ctx.send(f"Uploaded {len(self.gifts)} gifts")

    async def download_file(self, url: str, file_path: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(file_path, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
        with open(file_path, "r", encoding="utf8") as f:
            return f.read()

    @slash_command(name="list_gifts_for", description="List all gifts")
    @slash_option(
        name="auspice",
        description="The auspice to filter for",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            {"name": "Ahroun", "value": "Ahroun"},
            {"name": "Galliard", "value": "Galliard"},
            {"name": "Philodox", "value": "Philodox"},
            {"name": "Theurge", "value": "Theurge"},
            {"name": "Ragabash", "value": "Ragabash"},
        ],
    )
    @slash_option(
        name="tribe",
        description="The tribe to filter for",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            {"name": "Fianna", "value": "Fianna"},
            {"name": "Glaswandler", "value": "Glaswandler"},
            {"name": "Kinder Gaias", "value": "Kinder Gaias"},
            {"name": "Knochenbeißer", "value": "Knochenbeißer"},
            {"name": "Nachfahren des Fenris", "value": "Nachfahren des Fenris"},
            {"name": "Rote Klauen", "value": "Rote Klauen"},
            {"name": "Schattenlords", "value": "Schattenlords"},
            {"name": "Schwarze Furien", "value": "Schwarze Furien"},
            {"name": "Silberfänge", "value": "Silberfänge"},
            {"name": "Sternenträumer", "value": "Sternenträumer"},
            {"name": "Stille Wanderer", "value": "Stille Wanderer"},
            {"name": "Uktena", "value": "Uktena"},
            {"name": "Wendigo", "value": "Wendigo"},
            {"name": "Tänzer der schwarzen Spirale", "value": "Tänzer der schwarzen Spirale"},
        ],
    )
    @slash_option(
        name="breed",
        description="The breed to filter for",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            {"name": "Menschling", "value": "Menschling"},
            {"name": "Lupus", "value": "Lupus"},
            {"name": "Metis", "value": "Metis"},
        ],
    )
    @slash_option(
        name="rank",
        description="The rank to filter for",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            {"name": "Cliath", "value": "Cliath"},
            {"name": "Pflegling", "value": "Pflegling"},
            {"name": "Adren", "value": "Adren"},
            {"name": "Athro", "value": "Athro"},
            {"name": "Ältester", "value": "Ältester"},
            {"name": "Legende", "value": "Legende"},
        ],
    )
    async def list_gifts_for(
        self,
        ctx: SlashContext,
        auspice: str = None,
        tribe: str = None,
        breed: str = None,
        rank: str = None,
    ):
        """List all gifts."""
        buttons: list[Button] = []
        part_counter = 1
        print("list_gifts_for")
        print(f"auspice: {auspice}")
        print(f"tribe: {tribe}")
        print(f"breed: {breed}")
        print(f"rank: {rank}")
        for gift in self.gifts:
            if (
                (auspice is None or auspice.lower() in gift.available_for.lower())
                and (tribe is None or tribe.lower() in gift.available_for.lower())
                and (breed is None or breed.lower() in gift.available_for.lower())
                and (rank is None or rank.lower() in gift.available_for.lower())
            ):
                buttons.append(
                    Button(
                        label=gift.name,
                        style=ButtonStyle.PRIMARY,
                        custom_id=f"show_gift_{gift.name}",
                    )
                )
                print(f"Added {gift.name}")
                if len(buttons) >= 25:
                    print(f"Sent {part_counter} with {len(buttons)} buttons")
                    await ctx.send(f"Gifts {part_counter}", components=spread_to_rows(*buttons))
                    buttons = []
                    part_counter += 1
        if len(buttons) > 0:
            await ctx.send(f"Gifts {part_counter}", components=spread_to_rows(*buttons))
            part_counter += 1
        if part_counter == 1:
            await ctx.send(f"No gifts found for this filter ({len(self.gifts)} Gifts Total)")

    @component_callback(regex_pattern)
    async def show_gift_callback(self, ctx: ComponentContext):
        """Show gift description."""
        if match := regex_pattern.match(ctx.custom_id):
            gift_name = match.group(1)
            await self.display_gift(ctx, gift_name)
        else:
            await ctx.send(f"Could not find gift {ctx.custom_id}")
