"""This module contains the NSCGen extension with a command to generate random NSC characters."""
import random

from interactions import (
    Embed,
    Extension,
    LocalisedDesc,
    LocalisedName,
    OptionType,
    SlashContext,
    slash_command,
    slash_option,
)

import app.library.aengste as aengste
import app.library.charaktereigenschaften as charaktereigenschaften
import app.library.plaene as plaene
import app.localizer as localizer
from app.library.speciesnames import names as btw_names


class NSCGen(Extension):
    """An extension for generating random NSC characters."""
    async def async_start(self):
        """Print a message when the extension is started."""
        print("Starting NSCGen Extension")

    @slash_command(
        name="btw_new",
        description=LocalisedDesc(**localizer.translations("btw_new_description")),
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("mensch")),
        description=LocalisedDesc(**localizer.translations("mensch_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="mensch",
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("zwerg")),
        description=LocalisedDesc(**localizer.translations("zwerg_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="zwerg",
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("elf")),
        description=LocalisedDesc(**localizer.translations("elf_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="elf",
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("ork")),
        description=LocalisedDesc(**localizer.translations("ork_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="ork",
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("goblin")),
        description=LocalisedDesc(**localizer.translations("goblin_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="goblin",
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("oger")),
        description=LocalisedDesc(**localizer.translations("oger_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="oger",
    )
    @slash_option(
        name=LocalisedName(**localizer.translations("nymph")),
        description=LocalisedDesc(**localizer.translations("nymph_description")),
        opt_type=OptionType.BOOLEAN,
        required=False,
        argument_name="nymph",
    )
    @slash_option(
        name="count",
        description=LocalisedDesc(**localizer.translations("count_description")),
        opt_type=OptionType.INTEGER,
        required=False,
    )
    async def random_btw_nsc(
        self,
        ctx: SlashContext,
        mensch: bool = False,
        zwerg: bool = False,
        elf: bool = False,
        ork: bool = False,
        goblin: bool = False,
        oger: bool = False,
        nymph: bool = False,
        count: int = 1,
    ):
        """Generate a random NSC character."""
        available_species = []
        if mensch:
            available_species.append("Mensch")
        if zwerg:
            available_species.append("Zwerg")
        if elf:
            available_species.append("Elf")
        if ork:
            available_species.append("Ork")
        if goblin:
            available_species.append("Goblin")
        if oger:
            available_species.append("Oger")
        if nymph:
            available_species.append("Nymph")
        embeds = []
        for _ in range(count):
            if not available_species:
                species = localizer.translate(ctx.locale, "unbekannt")
                name = localizer.translate(ctx.locale, "unbekannt")
            else:
                species = random.choice(available_species)
                name = random.choice(btw_names[species])
            embed = Embed(
                title=name,
                description=", ".join(charaktereigenschaften.get_random() for _ in range(3)),
            )
            embed.add_field(
                name=localizer.translate(ctx.locale, "species"), value=species, inline=False
            )
            nsc_plaene = f"*{plaene.get_random_gross()}*"  # TODO: LOCALIZATION FLAG
            smallplans = []
            for _ in range(random.randint(0, 3)):
                new_plan = plaene.get_random_klein(exclude=smallplans)
                smallplans.append(new_plan)
                nsc_plaene += "\n" + new_plan
            embed.add_field(name=localizer.translate(ctx.locale, "pläne"), value=nsc_plaene)
            embed.add_field(
                name=localizer.translate(ctx.locale, "ängste"),
                value="\n".join(aengste.get_randoms(random.randint(1, 3))),
            )
            embeds.append(embed)
        await ctx.send(embeds=embeds, ephemeral=True)
