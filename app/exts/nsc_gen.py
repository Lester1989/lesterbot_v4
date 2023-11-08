from config import SCOPE_KWARG
from interactions import Embed, Extension, slash_command, slash_option, SlashContext, OptionType,SlashCommandChoice
import random
import library.aengste as aengste
import library.charaktereigenschaften as charaktereigenschaften
import library.plaene as plaene
from library.speciesnames import names as btw_names



class NSCGen(Extension):
    async def async_start(self):
        print("Starting NSCGen Extension")

    @slash_command(
        name="btw_new",
        description="Erstellt einen zufälligen NSC für Beyond the Wall",
        **SCOPE_KWARG)
    @slash_option(
                name="mensch",
                description="kann der NSC ein Mensch sein",
                opt_type=OptionType.BOOLEAN,
                required=False )
    @slash_option(
                name="zwerg",
                description="kann der NSC ein Zwerg sein",
                opt_type=OptionType.BOOLEAN,
                required=False )
    @slash_option(
                name="elf",
                description="kann der NSC ein Elf sein",
                opt_type=OptionType.BOOLEAN,
                required=False)
    @slash_option(
                name="ork",
                description="kann der NSC ein Ork sein",
                opt_type=OptionType.BOOLEAN,
                required=False)
    @slash_option(
                name="goblin",
                description="kann der NSC ein Goblin sein",
                opt_type=OptionType.BOOLEAN,
                required=False,)
    @slash_option(
                name="oger",
                description="kann der NSC ein Oger sein",
                opt_type=OptionType.BOOLEAN,
                required=False,)
    @slash_option(
                name="nymph",
                description="kann der NSC ein Nymph sein",
                opt_type=OptionType.BOOLEAN,
                required=False,)
    @slash_option(
                name="count",
                description="Wieviele NSC sollen erstellt werden?",
                opt_type=OptionType.INTEGER,
                required=False,
            )
    async def random_btw_nsc(
        self,
        context: SlashContext,
        mensch: bool = False,
        zwerg: bool = False,
        elf: bool = False,
        ork: bool = False,
        goblin: bool = False,
        oger: bool = False,
        nymph: bool = False,
        count:int = 1
    ):
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
                species = "Unbekannt"
                name = "Unbekannt"
            else:
                species = random.choice(available_species)
                name = random.choice(btw_names[species])
            embed = Embed(
                title=name,
                description=", ".join(
                    charaktereigenschaften.get_random() for _ in range(3)
                ),
            )
            embed.add_field(name="Species", value=species,inline=False)
            nsc_plaene = f"*{plaene.get_random_gross()}*"
            smallplans = []
            for _ in range(random.randint(0, 3)):
                new_plan = plaene.get_random_klein(exclude=smallplans)
                smallplans.append(new_plan)
                nsc_plaene += "\n" + new_plan
            embed.add_field(name="Pläne", value=nsc_plaene)
            embed.add_field(
                name="Ängste", value="\n".join(aengste.get_randoms(random.randint(1, 3)))
            )
            embeds.append(embed)
        await context.send(embeds=embeds, ephemeral=True)