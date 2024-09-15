"""Werewolf: The Apocalypse 20th Anniversary Edition extension for Polydice."""

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
    LocalisedDesc,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    component_callback,
    slash_command,
    slash_option,
    spread_to_rows,
)

import app.localizer as localizer
from app.library.polydice import (
    ExplodingBehavior,
    format_dice_success_result,
    roll_dice_successes,
)
from app.library.werewolf_gifts import Gift, load_gifts, parse_json

regex_pattern_gifts = re.compile(r"show_gift_(.*)")
regex_pattern_ww_repeat = re.compile(r"ww_repeat_(.*)")


class WerewolfW20(Extension):
    """An extension for Werewolf: The Apocalypse 20th Anniversary Edition."""

    gifts: list[Gift] = []
    gift_names: list[str] = []

    async def async_start(self):
        """Print a message when the extension is started."""
        self.gifts = load_gifts()
        self.gift_names = [gift.name.lower() for gift in self.gifts]
        print("Starting Werewolf Extension")

    @slash_command(
        name="ww", description=LocalisedDesc(**localizer.translations("ww_description"))
    )
    @slash_option(
        name="number",
        description=LocalisedDesc(**localizer.translations("number_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="difficulty",
        description=LocalisedDesc(**localizer.translations("difficulty_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="ones_cancel",
        description=LocalisedDesc(**localizer.translations("ones_cancel_description")),
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="specialty",
        description=LocalisedDesc(**localizer.translations("specialty_description")),
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="spent_willpower",
        description=LocalisedDesc(
            **localizer.translations("spent_willpower_description")
        ),
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
        exploding = ExplodingBehavior.PLUSSUCCESS if specialty else ExplodingBehavior.NONE
        result = roll_dice_successes(
            number,
            10,
            exploding,
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
            title=localizer.translate(
                ctx.locale,
                "rolling_number_dice_with_difficulty_difficulty",
                number=number,
                difficulty=difficulty,
            ),
            color=color,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "dice_results"),
            value="\n".join(
                [
                    format_dice_success_result(dice_result, difficulty, ones_cancel, exploding)
                    for dice_result in result.dice_results + result.extra_dice
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "successes"),
            value=f"{result.successes}",
            inline=False,
        )
        if spent_willpower:
            embed.set_footer(
                text=localizer.translate(ctx.locale, "willpower_spent_footer")
            )
        components = spread_to_rows(
            Button(
                label=localizer.translate(ctx.locale, "roll_again"),
                style=ButtonStyle.PRIMARY,
                custom_id=f"ww_repeat_{number}_{difficulty}_{ones_cancel}_{specialty}_{spent_willpower}",
            )
        )
        await ctx.send(embed=embed,components=components)

    @component_callback(regex_pattern_ww_repeat)
    async def ww_repeat(self, ctx: ComponentContext):
        """Rolls a number of dice and counts the number of successes."""
        if match := regex_pattern_ww_repeat.match(ctx.custom_id):
            number, difficulty, ones_cancel, specialty, spent_willpower = map(
                int, match.groups()
            )
            await self.ww(
                ctx,
                number=number,
                difficulty=difficulty,
                ones_cancel=bool(ones_cancel),
                specialty=bool(specialty),
                spent_willpower=bool(spent_willpower),
            )
        else:
            await ctx.send(
                localizer.translate(
                    ctx.locale,
                    "could_not_find_ww_repeat_ctxcustom_id",
                    ctxcustom_id=ctx.custom_id,
                )
            )

    @slash_command(
        name="show_gift",
        description=LocalisedDesc(**localizer.translations("show_gift_description")),
    )
    @slash_option(
        name="gift_name",
        description=LocalisedDesc(**localizer.translations("gift_name_description")),
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True,
    )
    async def show_gift(self, ctx: SlashContext, gift_name: str):
        """Show gift description."""
        return await self.display_gift(ctx, gift_name)

    async def display_gift(self, ctx: SlashContext, gift_name: str):
        """Display the gift description."""
        gift = next(
            (gift for gift in self.gifts if gift.name.lower() == gift_name.lower()),
            None,
        )
        if gift is None:
            await ctx.send(
                localizer.translate(
                    ctx.locale, "could_not_find_gift_gift_name", gift_name=gift_name
                )
            )
            return
        embed = Embed(
            title=gift.name, description=gift.description_fluff, color=0xFFFFFF
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "system"),
            value=gift.description_system,
            inline=False,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "available_for"),
            value=gift.available_for,
            inline=False,
        )
        await ctx.send(embed=embed)

    @show_gift.autocomplete("gift_name")
    async def gift_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocomplete gift names."""
        string_option_input = ctx.input_text

        result = [
            SlashCommandChoice(name=gift_name, value=gift_name)
            for gift_name in self.gift_names
            if string_option_input.lower() in gift_name
        ][:10]
        await ctx.send(choices=result)

    @slash_command(
        name="upload_gifts",
        description=LocalisedDesc(**localizer.translations("upload_gifts_description")),
    )
    @slash_option(
        name="file",
        description=LocalisedDesc(**localizer.translations("file_description")),
        required=True,
        opt_type=OptionType.ATTACHMENT,
    )
    async def upload_gifts(self, ctx: SlashContext, file: Attachment):
        """Upload gifts from a CSV file."""
        content = await self.download_file(file.url, file.filename)
        self.gifts = parse_json(content)
        self.gift_names = [gift.name.lower() for gift in self.gifts]
        await ctx.send(
            localizer.translate(
                ctx.locale, "uploaded_lenselfgifts_gifts", lenselfgifts=len(self.gifts)
            )
        )

    async def download_file(self, url: str, file_path: str):
        """Download a file from a URL."""
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

    @slash_command(
        name="list_gifts_for",
        description=LocalisedDesc(
            **localizer.translations("list_gifts_for_description")
        ),
    )
    @slash_option(
        name="auspice",
        description=LocalisedDesc(
            **localizer.translations("the_auspice_to_filter_for")
        ),
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Ahroun", value="Ahroun"),
            SlashCommandChoice(name="Galliard", value="Galliard"),
            SlashCommandChoice(name="Philodox", value="Philodox"),
            SlashCommandChoice(name="Theurge", value="Theurge"),
            SlashCommandChoice(name="Ragabash", value="Ragabash"),
        ],
    )
    @slash_option(
        name="tribe",
        description=LocalisedDesc(**localizer.translations("the_tribe_to_filter_for")),
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Fianna", value="Fianna"),
            SlashCommandChoice(name="Glaswandler", value="Glaswandler"),
            SlashCommandChoice(name="Kinder Gaias", value="Kinder Gaias"),
            SlashCommandChoice(name="Knochenbeißer", value="Knochenbeißer"),
            SlashCommandChoice(
                name="Nachfahren des Fenris", value="Nachfahren des Fenris"
            ),
            SlashCommandChoice(name="Rote Klauen", value="Rote Klauen"),
            SlashCommandChoice(name="Schattenlords", value="Schattenlords"),
            SlashCommandChoice(name="Schwarze Furien", value="Schwarze Furien"),
            SlashCommandChoice(name="Silberfänge", value="Silberfänge"),
            SlashCommandChoice(name="Sternenträumer", value="Sternenträumer"),
            SlashCommandChoice(name="Stille Wanderer", value="Stille Wanderer"),
            SlashCommandChoice(name="Uktena", value="Uktena"),
            SlashCommandChoice(name="Wendigo", value="Wendigo"),
            SlashCommandChoice(
                name="Tänzer der schwarzen Spirale",
                value="Tänzer der schwarzen Spirale",
            ),
        ],
    )
    @slash_option(
        name="breed",
        description=LocalisedDesc(**localizer.translations("the_breed_to_filter_for")),
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Menschling", value="Menschling"),
            SlashCommandChoice(name="Lupus", value="Lupus"),
            SlashCommandChoice(name="Metis", value="Metis"),
        ],
    )
    @slash_option(
        name="rank",
        description=LocalisedDesc(**localizer.translations("the_rank_to_filter_for")),
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Cliath", value="Cliath"),
            SlashCommandChoice(name="Pflegling", value="Pflegling"),
            SlashCommandChoice(name="Adren", value="Adren"),
            SlashCommandChoice(name="Athro", value="Athro"),
            SlashCommandChoice(name="Ältester", value="Ältester"),
            SlashCommandChoice(name="Legende", value="Legende"),
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
                if len(buttons) >= 25:
                    await ctx.send(
                        localizer.translate(
                            ctx.locale, "gifts_part_counter", part_counter=part_counter
                        ),
                        components=spread_to_rows(*buttons),
                    )
                    buttons = []
                    part_counter += 1
        if len(buttons) > 0:
            await ctx.send(
                localizer.translate(
                    ctx.locale, "gifts_part_counter", part_counter=part_counter
                ),
                components=spread_to_rows(*buttons),
            )
            part_counter += 1
        if part_counter == 1:
            await ctx.send(
                localizer.translate(
                    ctx.locale,
                    "no_gifts_found_for_this_filter_lenselfgifts_gifts_total",
                    lenselfgifts=len(self.gifts),
                )
            )

    @component_callback(regex_pattern_gifts)
    async def show_gift_callback(self, ctx: ComponentContext):
        """Show gift description."""
        if match := regex_pattern_gifts.match(ctx.custom_id):
            gift_name = match.group(1)
            await self.display_gift(ctx, gift_name)
        else:
            await ctx.send(
                localizer.translate(
                    ctx.locale,
                    "could_not_find_gift_ctxcustom_id",
                    ctxcustom_id=ctx.custom_id,
                )
            )
