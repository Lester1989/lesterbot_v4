from interactions import (
    AutocompleteContext,
    BaseContext,
    Embed,
    Extension,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    User,
    check,
    slash_command,
    slash_option,
)

from app.library.charsheet import (
    AttributeType,
    CategorySetting,
    CategoryUser,
    CharacterHeader,
    CharactersheetEntry,
    GroupState,
    ModificationState,
    RuleSystemRolls,
    RuleSystemSuggestions,
    SheetModification,
)
from app.library.complex_dice_parser import Parser
from app.library.polydice import ComplexPool


async def is_gm(context: BaseContext):
    return CategoryUser.get(int(context.channel.category.id), int(context.author.id)).is_gm


def embed_length(embed: Embed):
    """Calculates the length of an embed."""
    return (
        len(embed.title)
        + len(embed.description)
        + sum(len(field.name) + len(field.value) for field in embed.fields)
        + (len(embed.footer.text) if embed.footer else 0)
        + (len(embed.author.name) if embed.author else 0)
    )


class CharSheetManager(Extension):
    async def async_start(self):
        print("Starting CharSheetManager Extension")

    def show_group_info(self, ctx: SlashContext) -> Embed:
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        users = CategoryUser.get_by_category(int(ctx.channel.category.id))
        embed = Embed(
            title=f"Group {ctx.channel.category.name} {'(forming)' if settings.state == GroupState.CREATING else ''}",
            color=0xFFFFFF,
        )
        embed.add_field(name="Rule System", value=settings.rule_system)
        embed.add_field(
            name="GMs",
            value="\n".join(
                ctx.guild.get_member(int(user.user_id)).display_name for user in users if user.is_gm
            ),
        )
        if any(not user.is_gm for user in users):
            embed.add_field(
                name="Players",
                value="\n".join(
                    ctx.guild.get_member(int(user.user_id)).display_name
                    for user in users
                    if not user.is_gm
                ),
            )
        else:
            embed.add_field(name="Players", value="invite players with /add_player")
        embed.add_field(
            name="Character Changes",
            value="Need GM approval after start"
            if settings.changes_need_approval
            else "Approved by default",
        )
        if settings.hidden_rolls_allowed:
            embed.add_field(name="Hidden Rolls", value="Allowed")
        if settings.web_interface_enabled:
            embed.add_field(name="Web Interface", value="Coming soon")

        return embed

    @slash_command(
        name="start_group",
        description="Opens a group, creates default settings and makes you GM",
    )
    @slash_option(
        name="rule_system",
        description="The rule system to use",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def start_group(self, ctx: SlashContext, rule_system: str):
        """Opens a group, creates default settings and makes you GM."""
        settings = CategorySetting.create(int(ctx.channel.category.id))
        CategorySetting.update(settings.category_id, rule_system=rule_system)
        CategoryUser.create(int(ctx.channel.category.id), int(ctx.author.id), is_gm=True)
        await ctx.send("Group created", embed=self.show_group_info(ctx))

    @slash_command(name="add_player", description="Joins a player to the group")
    @slash_option(
        name="player", description="The player to add", required=True, opt_type=OptionType.USER
    )
    @check(is_gm)
    async def add_player(self, ctx: SlashContext, player: User):
        """Joins a player to the group."""
        CategoryUser.create(int(ctx.channel.category.id), int(player.id), is_gm=False)
        await ctx.send("Player added", embed=self.show_group_info(ctx))

    @slash_command(name="remove_player", description="Removes a player from the group")
    @slash_option(
        name="player", description="The player to remove", required=True, opt_type=OptionType.USER
    )
    @check(is_gm)
    async def remove_player(self, ctx: SlashContext, player: User):
        """Removes a player from the group."""
        CategoryUser.delete(int(ctx.channel.category.id), int(player.id))
        await ctx.send("Player removed", embed=self.show_group_info(ctx))

    @slash_command(name="add_gm", description="Makes a player GM")
    @slash_option(
        name="player", description="The player to make GM", required=True, opt_type=OptionType.USER
    )
    @check(is_gm)
    async def add_gm(self, ctx: SlashContext, player: User):
        """Makes a player GM."""
        CategoryUser.update(int(ctx.channel.category.id), int(player.id), is_gm=True)
        await ctx.send("Player made GM", embed=self.show_group_info(ctx))

    @slash_command(name="resign_gm", description="Removes GM status from you")
    @check(is_gm)
    async def resign_gm(self, ctx: SlashContext):
        """Removes GM status from you."""
        CategoryUser.update(int(ctx.channel.category.id), int(ctx.author.id), is_gm=False)
        await ctx.send("GM status removed", embed=self.show_group_info(ctx))

    @slash_command(name="show_group", description="Shows group info")
    async def show_group(self, ctx: SlashContext):
        """Shows group info."""
        await ctx.send(embed=self.show_group_info(ctx))

    @slash_command(name="set_rule_system", description="Sets the rule system to use")
    @slash_option(
        name="rule_system",
        description="The rule system to use",
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def set_rule_system(self, ctx: SlashContext, rule_system: str):
        """Sets the rule system to use."""
        CategorySetting.update(int(ctx.channel.category.id), rule_system=rule_system)
        await ctx.send("Rule system set", embed=self.show_group_info(ctx))

    @slash_command(
        name="creation_finished", description="Stops free character creation and starts the game"
    )
    @check(is_gm)
    async def creation_finished(self, ctx: SlashContext):
        """Stops free character creation and starts the game."""
        CategorySetting.update(int(ctx.channel.category.id), state=GroupState.STARTED)
        await ctx.send("Creation finished", embed=self.show_group_info(ctx))

    def chunk_list(self, items: list[str], join_char: str = "\n", max_length: int = 1000):
        current_string = ""
        for item in items:
            if len(current_string + item) > max_length:
                yield current_string
                current_string = ""
            current_string += item + join_char
        yield current_string

    def display_character(self, ctx: SlashContext, character: CharacterHeader) -> Embed:
        results = []
        embed = Embed(
            title=character.name,
            description=character.concept,
            color=0xFFFFFF,
        )
        if character.image_url:
            embed.set_image(url=character.image_url)
        char_sheet_entries = (
            CharactersheetEntry.get(character.user_id, int(ctx.channel.category.id), character.name)
            or []
        )
        embed.add_field(name="Description", value=character.description)
        embed.add_field(name="Player", value=f"<@{character.user_id}>")
        field_count = 2
        grouped_entries: dict[str, list[str]] = {
            "Attributes": [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.ATTRIBUTE
            ],
            "Skills": [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.SKILL
            ],
            "Specialties": [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.SPECIALTY
            ],
            "General": [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.GENERAL
            ],
            "Unknown": [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.UNKNOWN
            ],
        }
        for group_name, group_lines in grouped_entries.items():
            for i, char_entry_block in enumerate(self.chunk_list(group_lines)):
                if (
                    field_count >= 24
                    or embed_length(embed) + len(char_entry_block) + len(f"{group_name} {i+1}")
                    >= 5900
                ):
                    results.append(embed)
                    embed = Embed(
                        title=f"{character.name} (continued)",
                        description=character.concept,
                        color=0xFFFFFF,
                    )
                    field_count = 0
                embed.add_field(name=f"{group_name} {i+1}", value=char_entry_block or "...")
                field_count += 1
        results.append(embed)
        return results

    async def character_name_autocomplete(
        self, ctx: AutocompleteContext, gm_see_all: bool = False, everyone_see_all: bool = False
    ):
        # TODO cache the character names
        string_option_input = ctx.input_text
        print(f"Autocomplete for {string_option_input}")
        if everyone_see_all or (gm_see_all and is_gm(ctx)):
            headers = CharacterHeader.get_by_category(int(ctx.channel.category.id))
        else:
            headers = CharacterHeader.get_available(
                int(ctx.author.id), int(ctx.channel.category.id)
            )
        await ctx.send(
            choices=[
                {"name": header.name, "value": header.name}
                for header in headers
                if string_option_input.lower() in header.name
            ][:10]
        )

    @slash_command(name="create_character", description="Creates a character sheet header")
    @slash_option(
        name="name",
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="concept",
        description="Short description of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="description",
        description="Long description of the character",
        required=False,
        opt_type=OptionType.STRING,
    )
    async def create_character(
        self, ctx: SlashContext, name: str, concept: str, description: str = None
    ):
        """Creates a character sheet header."""
        character = CharacterHeader.create(
            int(ctx.author.id), int(ctx.channel.category.id), name, concept, description
        )
        await ctx.send("Character created", embed=self.display_character(ctx, character))

    @slash_command(name="update_character", description="Updates a character sheet header")
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="concept",
        description="Short description of the character",
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="description",
        description="Long description of the character",
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="image_url",
        description="Image to show for the character",
        required=False,
        opt_type=OptionType.STRING,
    )
    async def update_character(
        self,
        ctx: SlashContext,
        name: str,
        concept: str = None,
        description: str = None,
        image_url: str = None,
    ):
        """Updates a character sheet header."""
        character = CharacterHeader.update(name, concept, description, image_url)
        await ctx.send("Character updated", embed=self.display_character(ctx, character))

    @update_character.autocomplete("name")
    async def update_character_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="delete_character", description="Deletes a character sheet header and all entries"
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="confirm",
        description="Type 'confirm' to confirm the deletion, cannot be undone",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def delete_character(self, ctx: SlashContext, name: str, confirm: str):
        """Deletes a character sheet header and all entries."""
        if confirm != "confirm":
            await ctx.send("Deletion not confirmed")
            return
        CharacterHeader.delete(int(ctx.author_id), int(ctx.channel.category.id), name)
        CharactersheetEntry.delete(int(ctx.author_id), int(ctx.channel.category.id), name)
        await ctx.send("Character deleted")

    @delete_character.autocomplete("name")
    async def delete_character_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx)

    @slash_command(name="show_character", description="Shows a character sheet header")
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def show_character(self, ctx: SlashContext, name: str):
        """Shows a character sheet header."""
        character = CharacterHeader.get(int(ctx.author_id), int(ctx.channel.category.id), name)
        await ctx.send(embed=self.display_character(ctx, character))

    @show_character.autocomplete("name")
    async def show_character_name_autocomplete(self, ctx: AutocompleteContext):
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        await self.character_name_autocomplete(ctx, True, not settings.character_hidden)

    @slash_command(name="add_attribute", description="Adds an attribute to a character sheet")
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_name",
        description="The name of the attribute",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_value",
        description="The value of the attribute",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_type",
        description="The type of the attribute",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Attribute", value="Attribute"),
            SlashCommandChoice(name="Skill", value="Skill"),
            SlashCommandChoice(name="Specialty", value="Specialty"),
            SlashCommandChoice(name="General", value="General"),
        ],
    )
    @slash_option(
        name="override",
        description="Overrides an existing attribute",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    async def add_attribute(
        self,
        ctx: SlashContext,
        name: str,
        attribute_name: str,
        attribute_value: str,
        attribute_type: str = "Unknown",
        override: bool = False,
    ):
        """Adds an attribute to a character sheet."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        if settings.state == GroupState.STARTED or not settings.changes_need_approval or is_gm(ctx):
            if override:
                CharactersheetEntry.remove_key(
                    int(ctx.author_id), int(ctx.channel.category.id), name, attribute_name
                )
            CharactersheetEntry.create(
                int(ctx.author_id),
                int(ctx.channel.category.id),
                name,
                attribute_name,
                attribute_value,
                AttributeType(attribute_type),
            )
            await ctx.send("Attribute added")
        else:
            if override:
                SheetModification.delete(
                    int(ctx.author_id), int(ctx.channel.category.id), name, attribute_name
                )
            SheetModification.create(
                int(ctx.author_id),
                int(ctx.channel.category.id),
                name,
                attribute_name,
                attribute_value,
                AttributeType(attribute_type),
                "Attribute added",
            )
            await ctx.send("Attribute added, waiting for approval by your gm")

    @add_attribute.autocomplete("name")
    async def add_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="list_pending_changes", description="Lists pending changes for a character sheet"
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def list_pending_changes(self, ctx: SlashContext, name: str):
        """Lists pending changes for a character sheet."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send("No pending changes")
            return
        changes: dict[str, SheetModification] = {
            f"{change.sheet_key}": change
            for change in SheetModification.get(
                int(ctx.author_id), int(ctx.channel.category.id), name
            )
            if change.status == ModificationState.PENDING
        }
        if not changes:
            await ctx.send("No pending changes")
            return
        original_character: dict[str, CharactersheetEntry] = {
            f"{entry.sheet_key}": entry
            for entry in CharactersheetEntry.get(
                int(ctx.author_id), int(ctx.channel.category.id), name
            )
            if entry.sheet_key in changes
        }
        embed = Embed(
            title=f"Pending changes for {name}",
            color=0xFFFFFF,
        )
        changing_types = {change.attribute_type for change in changes.values()}
        change_lists: dict[AttributeType, list[str]] = {
            attribute_type: [
                f"{change.sheet_key}: {original_character[change.sheet_key].value} -> {change.value} "
                for change in changes.values()
                if change.attribute_type == attribute_type
            ]
            for attribute_type in changing_types
        }
        for attribute_type, change_list in change_lists.items():
            for i, change_block in enumerate(self.chunk_list(change_list)):
                embed.add_field(name=f"{attribute_type} {i+1}", value=change_block)
        action_advice = (
            "wait for your GM to approve them"
            if is_gm(ctx)
            else "approve them all with /approve_all_changes or /reject_all_changes\n\n Or handle them one by one with /approve_change or /reject_change"
        )
        await ctx.send(action_advice, embed=embed)

    @list_pending_changes.autocomplete("name")
    async def list_pending_changes_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="approve_all_changes", description="Approves all pending changes for a character sheet"
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def approve_all_changes(self, ctx: SlashContext, name: str):
        """Approves all pending changes for a character sheet."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send("No pending changes")
            return
        changes = SheetModification.get(int(ctx.author_id), int(ctx.channel.category.id), name)
        change_count = 0
        for change in changes:
            if change.status == ModificationState.PENDING:
                change_count += 1
                CharactersheetEntry.update(
                    int(ctx.author_id),
                    int(ctx.channel.category.id),
                    name,
                    change.sheet_key,
                    change.value,
                    change.attribute_type,
                )
                SheetModification.update(
                    int(ctx.author_id),
                    int(ctx.channel.category.id),
                    name,
                    change.sheet_key,
                    status=ModificationState.APPROVED,
                )
        await ctx.send(f"All {change_count} changes approved for {name}")

    @approve_all_changes.autocomplete("name")
    async def approve_all_changes_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="reject_all_changes", description="Rejects all pending changes for a character sheet"
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="reason",
        description="The reason for the rejection",
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def reject_all_changes(self, ctx: SlashContext, name: str, reason: str):
        """Rejects all pending changes for a character sheet."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send("No pending changes")
            return
        changes = SheetModification.get(int(ctx.author_id), int(ctx.channel.category.id), name)
        change_count = 0
        for change in changes:
            if change.status == ModificationState.PENDING:
                change_count += 1
                SheetModification.update(
                    int(ctx.author_id),
                    int(ctx.channel.category.id),
                    name,
                    change.sheet_key,
                    status=ModificationState.REJECTED,
                    comment=reason,
                )
        await ctx.send(f"All {change_count} changes rejected for {name}")

    @reject_all_changes.autocomplete("name")
    async def reject_all_changes_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    async def change_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        char_name = ctx.kwargs.get("name")
        if not char_name:
            await ctx.send(
                choices=[
                    {
                        "name": "No character name needed for autocompletion",
                        "value": "No character name needed for autocompletion",
                    }
                ]
            )
            return
        changes = SheetModification.get(int(ctx.author_id), int(ctx.channel.category.id), char_name)

        await ctx.send(
            choices=[
                {"name": change.sheet_key, "value": change.sheet_key}
                for change in changes
                if change.status == ModificationState.PENDING
                and ctx.input_text.lower() in change.sheet_key.lower()
            ][:10]
        )

    @slash_command(
        name="approve_change", description="Approves a pending change for a character sheet"
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_name",
        autocomplete=True,
        description="The name of the attribute",
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def approve_change(self, ctx: SlashContext, name: str, attribute_name: str):
        """Approves a pending change for a character sheet."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send("No pending changes")
            return
        change = SheetModification.get_key(
            int(ctx.author_id), int(ctx.channel.category.id), name, attribute_name
        )
        if change and change.status == ModificationState.PENDING:
            CharactersheetEntry.update(
                int(ctx.author_id),
                int(ctx.channel.category.id),
                name,
                change.sheet_key,
                change.value,
                change.attribute_type,
            )
            SheetModification.update(
                int(ctx.author_id),
                int(ctx.channel.category.id),
                name,
                attribute_name,
                status=ModificationState.APPROVED,
            )
            await ctx.send(f"Change approved for {name}")
            return
        await ctx.send("No pending change found")

    @approve_change.autocomplete("name")
    async def approve_change_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    @approve_change.autocomplete("attribute_name")
    async def approve_change_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        self.change_attribute_name_autocomplete(ctx)

    @slash_command(
        name="reject_change", description="Rejects a pending change for a character sheet"
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description="The name of the character",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_name",
        autocomplete=True,
        description="The name of the attribute",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="reason",
        description="The reason for the rejection",
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def reject_change(self, ctx: SlashContext, name: str, attribute_name: str, reason: str):
        """Rejects a pending change for a character sheet."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send("No pending changes")
            return
        change = SheetModification.get_key(
            int(ctx.author_id), int(ctx.channel.category.id), name, attribute_name
        )
        if change and change.status == ModificationState.PENDING:
            SheetModification.update(
                int(ctx.author_id),
                int(ctx.channel.category.id),
                name,
                attribute_name,
                status=ModificationState.REJECTED,
                comment=reason,
            )
            await ctx.send(f"Change rejected for {name}")
            return
        await ctx.send("No pending change found")

    @reject_change.autocomplete("name")
    async def reject_change_name_autocomplete(self, ctx: AutocompleteContext):
        await self.character_name_autocomplete(ctx, True)

    @reject_change.autocomplete("attribute_name")
    async def reject_change_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        self.change_attribute_name_autocomplete(ctx)

    @slash_command(
        name="gm_roll_initiative", description="Rolls initiative for all players and GMs"
    )
    @slash_option(
        name="nsc_slots",
        description="The number of NPC slots if more than 1",
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="npc_roll",
        description="The roll for the NPCs (see /roll_help)",
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="hidden",
        description="If the rolls should be hidden from players",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @check(is_gm)
    async def gm_roll_initiative(
        self, ctx: SlashContext, npc_slots: int = 0, npc_roll: str = "", hidden: bool = False
    ):
        """Rolls initiative for all players and GMs."""
        settings = CategorySetting.get_by_category(int(ctx.channel.category.id))
        initiative_rule = RuleSystemRolls.get(settings.rule_system, "INITIATIVE")
        if not initiative_rule:
            await ctx.send(f"No initiative rule found for {settings.rule_system}")
            return
        if npc_slots and not npc_roll:
            await ctx.send("Please provide a roll for the NPCs")
            return

        characters = CharacterHeader.get_by_category(int(ctx.channel.category.id))
        result = "**Initiative Rolls**\n"
        player_rolls: dict[str, ComplexPool] = {}
        for player_id_char_name, character_list in characters.items():
            player_id, char_name = player_id_char_name
            for character in character_list:
                if character.is_inactive:
                    continue
                sheet_entries: dict[str, int] = {
                    entry.sheet_key: entry.value
                    for entry in CharactersheetEntry.get(
                        player_id, int(ctx.channel.category.id), char_name
                    )
                    if entry.sheet_key in initiative_rule.needed_sheet_values
                }
                if len(sheet_entries) != len(initiative_rule.needed_sheet_values):
                    await ctx.send(
                        f"Missing values for {character.name}: {', '.join(initiative_rule.needed_sheet_values - set(sheet_entries.keys()))}"
                    )
                    continue
                player_rolls[char_name] = Parser(initiative_rule.eval(sheet_entries)).build_pool()
        for i in range(npc_slots):
            player_rolls[f"NPC {i+1}"] = Parser(npc_roll).build_pool()
        results = [
            (player_name, player_pool.roll()) for player_name, player_pool in player_rolls.items()
        ]
        for player_name, player_roll in sorted(results, key=lambda x: x[1], reverse=True):
            result += f"{player_name}: {player_roll}\n"
        await ctx.send(result, ephemeral=hidden)
