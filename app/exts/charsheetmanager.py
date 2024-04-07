"""This module contains the CharSheetManager extension, which provides commands for managing character sheets."""

from interactions import (
    AutocompleteContext,
    BaseContext,
    Embed,
    Extension,
    LocalisedDesc,
    LocalisedName,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    User,
    check,
    slash_command,
    slash_option,
)

import app.localizer as localizer
from app.library.charsheet import (
    AttributeType,
    CategorySetting,
    CategoryUser,
    CharacterHeader,
    CharactersheetEntry,
    GroupState,
    ModificationState,
    RuleSystemRolls,
    SheetModification,
)
from app.library.complex_dice_parser import Parser
from app.library.polydice import ComplexPool


async def is_gm(context: BaseContext):
    """Checks if the user is a GM."""
    return CategoryUser.get(
        str(context.channel.category.id), str(context.author.id)
    ).is_gm


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
    """Extension for managing character sheets."""

    async def async_start(self):
        """Prints a message when the extension is started."""
        print("Starting CharSheetManager Extension")

    def show_group_info(self, ctx: SlashContext) -> Embed:
        """Shows group info."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        users = CategoryUser.get_by_category(str(ctx.channel.category.id))
        embed = Embed(
            title=localizer.translate(
                ctx.locale,
                "group_ctxchannelcategoryname_forming_if_settingsstate__groupstatecreating_else_",
                ctxchannelcategoryname=ctx.channel.category.name,
                forming_if_settingsstate__groupstatecreating_else_=localizer.translate(
                    ctx.locale, "forming"
                )
                if settings.state == GroupState.CREATING
                else "",
            ),
            color=0xFFFFFF,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "rule_system"),
            value=settings.rule_system,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "gms"),
            value="\n".join(
                ctx.guild.get_member(str(user.user_id)).display_name
                for user in users
                if user.is_gm
            ),
        )
        characters: dict[str, list[str]] = {}
        for user_id, char_name in CharacterHeader.get_by_category(
            str(ctx.channel.category.id)
        ):
            if user_id not in characters:
                characters[user_id] = []
            characters[user_id].append(char_name)
        embed.add_field(
            name=localizer.translate(ctx.locale, "characters"),
            value="\n".join(
                f"{ctx.guild.get_member(str(user_id)).display_name} ({','.join(char_names)})"
                for user_id, char_names in characters.items()
            )
            if characters
            else localizer.translate(ctx.locale, "no_characters_created"),
        )
        if any(not user.is_gm for user in users):
            embed.add_field(
                name=localizer.translate(ctx.locale, "players"),
                value="\n".join(
                    f"{ctx.guild.get_member(str(user.user_id)).display_name} ({','.join(characters.get(str(user.user_id),['-'])) })"
                    for user in users
                    if not user.is_gm
                ),
            )
        else:
            embed.add_field(
                name=localizer.translate(ctx.locale, "players"),
                value=localizer.translate(ctx.locale, "invite_players_with_add_player"),
            )
        embed.add_field(
            name=localizer.translate(ctx.locale, "character_changes"),
            value=localizer.translate(ctx.locale, "need_gm_approval_after_start")
            if settings.changes_need_approval
            else localizer.translate(ctx.locale, "approved_by_default"),
        )
        if settings.hidden_rolls_allowed:
            embed.add_field(
                name=localizer.translate(ctx.locale, "hidden_rolls"),
                value=localizer.translate(ctx.locale, "allowed"),
            )
        if settings.web_interface_enabled:
            embed.add_field(
                name=localizer.translate(ctx.locale, "web_interface"),
                value=localizer.translate(ctx.locale, "coming_soon"),
            )

        return embed

    @slash_command(
        name="start_group",
        description=LocalisedDesc(**localizer.translations("start_group_description")),
    )
    @slash_option(
        name="rule_system",
        description=LocalisedDesc(**localizer.translations("rule_system_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    async def start_group(self, ctx: SlashContext, rule_system: str):
        """Opens a group, creates default settings and makes you GM."""
        settings = CategorySetting.create(str(ctx.channel.category.id))
        CategorySetting.update(settings.category_id, rule_system=rule_system)
        CategoryUser.create(
            str(ctx.channel.category.id), str(ctx.author.id), is_gm=True
        )
        await ctx.send(
            localizer.translate(ctx.locale, "group_created"),
            embed=self.show_group_info(ctx),
        )

    @slash_command(
        name="add_player",
        description=LocalisedDesc(**localizer.translations("add_player_description")),
    )
    @slash_option(
        name="player",
        description=LocalisedDesc(**localizer.translations("player_description")),
        required=True,
        opt_type=OptionType.USER,
    )
    @check(is_gm)
    async def add_player(self, ctx: SlashContext, player: User):
        """Joins a player to the group."""
        CategoryUser.create(str(ctx.channel.category.id), str(player.id), is_gm=False)
        await ctx.send(
            localizer.translate(ctx.locale, "player_added"),
            embed=self.show_group_info(ctx),
        )

    @slash_command(
        name="remove_player",
        description=LocalisedDesc(
            **localizer.translations("remove_player_description")
        ),
    )
    @slash_option(
        name="player",
        description=LocalisedDesc(**localizer.translations("player_description")),
        required=True,
        opt_type=OptionType.USER,
    )
    @check(is_gm)
    async def remove_player(self, ctx: SlashContext, player: User):
        """Removes a player from the group."""
        CategoryUser.delete(str(ctx.channel.category.id), str(player.id))
        await ctx.send(
            localizer.translate(ctx.locale, "player_removed"),
            embed=self.show_group_info(ctx),
        )

    @slash_command(
        name="add_gm",
        description=LocalisedDesc(**localizer.translations("add_gm_description")),
    )
    @slash_option(
        name="player",
        description=LocalisedDesc(**localizer.translations("player_description")),
        required=True,
        opt_type=OptionType.USER,
    )
    @check(is_gm)
    async def add_gm(self, ctx: SlashContext, player: User):
        """Makes a player GM."""
        CategoryUser.update(str(ctx.channel.category.id), str(player.id), is_gm=True)
        await ctx.send(
            localizer.translate(ctx.locale, "player_made_gm"),
            embed=self.show_group_info(ctx),
        )

    @slash_command(
        name="resign_gm",
        description=LocalisedDesc(**localizer.translations("resign_gm_description")),
    )
    @check(is_gm)
    async def resign_gm(self, ctx: SlashContext):
        """Removes GM status from you."""
        CategoryUser.update(
            str(ctx.channel.category.id), str(ctx.author.id), is_gm=False
        )
        await ctx.send(
            localizer.translate(ctx.locale, "gm_status_removed"),
            embed=self.show_group_info(ctx),
        )

    @slash_command(
        name="show_group",
        description=LocalisedDesc(**localizer.translations("show_group_description")),
    )
    async def show_group(self, ctx: SlashContext):
        """Shows group info."""
        await ctx.send(embed=self.show_group_info(ctx))

    @slash_command(
        name="set_rule_system",
        description=LocalisedDesc(
            **localizer.translations("set_rule_system_description")
        ),
    )
    @slash_option(
        name="rule_system",
        description=LocalisedDesc(**localizer.translations("rule_system_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def set_rule_system(self, ctx: SlashContext, rule_system: str):
        """Sets the rule system to use."""
        CategorySetting.update(str(ctx.channel.category.id), rule_system=rule_system)
        await ctx.send(
            localizer.translate(ctx.locale, "rule_system_set"),
            embed=self.show_group_info(ctx),
        )

    @slash_command(
        name="creation_finished",
        description=LocalisedDesc(
            **localizer.translations("creation_finished_description")
        ),
    )
    @check(is_gm)
    async def creation_finished(self, ctx: SlashContext):
        """Stops free character creation and starts the game."""
        CategorySetting.update(str(ctx.channel.category.id), state=GroupState.STARTED)
        await ctx.send(
            localizer.translate(ctx.locale, "creation_finished"),
            embed=self.show_group_info(ctx),
        )

    def chunk_list(
        self, items: list[str], join_char: str = "\n", max_length: int = 1000
    ):
        """Chunks a list of strings into strings of a maximum length."""
        current_string = ""
        for item in items:
            if len(current_string + item) > max_length:
                yield current_string
                current_string = ""
            current_string += item + join_char
        yield current_string

    def display_character(self, ctx: SlashContext, character: CharacterHeader) -> Embed:
        """Displays a character sheet."""
        results = []
        embed = Embed(
            title=character.name,
            description=character.concept,
            color=0xFFFFFF,
        )
        if character.image_url:
            embed.set_image(url=character.image_url)
        char_sheet_entries = (
            CharactersheetEntry.get(
                character.user_id, str(ctx.channel.category.id), character.name
            )
            or []
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "description"),
            value=character.description,
        )
        embed.add_field(
            name=localizer.translate(ctx.locale, "player"),
            value=f"<@{character.user_id}>",
        )
        field_count = 2
        grouped_entries: dict[str, list[str]] = {
            localizer.translate(ctx.locale, "attributes"): [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.ATTRIBUTE
            ],
            localizer.translate(ctx.locale, "skills"): [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.SKILL
            ],
            localizer.translate(ctx.locale, "specialties"): [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.SPECIALTY
            ],
            localizer.translate(ctx.locale, "general"): [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.GENERAL
            ],
            localizer.translate(ctx.locale, "unknown"): [
                f"{entry.sheet_key}: {entry.value}"
                for entry in char_sheet_entries
                if entry.attribute_type == AttributeType.UNKNOWN
            ],
        }
        for group_name, group_lines in grouped_entries.items():
            for i, char_entry_block in enumerate(self.chunk_list(group_lines)):
                if (
                    field_count >= 24
                    or embed_length(embed)
                    + len(char_entry_block)
                    + len(f"{group_name} {i+1}")
                    >= 5900
                ):
                    results.append(embed)
                    embed = Embed(
                        title=localizer.translate(
                            ctx.locale,
                            "charactername_continued",
                            charactername=character.name,
                        ),
                        description=character.concept,
                        color=0xFFFFFF,
                    )
                    field_count = 0
                if char_entry_block:
                    embed.add_field(
                        name=f"{group_name} {i+1}", value=char_entry_block or "..."
                    )
                    field_count += 1
        results.append(embed)
        return results

    async def character_name_autocomplete(
        self,
        ctx: AutocompleteContext,
        gm_see_all: bool = False,
        everyone_see_all: bool = False,
    ):
        """Autocompletes character names."""
        string_option_input = ctx.input_text
        if everyone_see_all or (gm_see_all and await is_gm(ctx)):
            headers = CharacterHeader.get_by_category(str(ctx.channel.category.id))
        else:
            headers = CharacterHeader.get_available(
                str(ctx.author.id), str(ctx.channel.category.id)
            )
        await ctx.send(
            choices=[
                {"name": header.name, "value": header.name}
                for header in headers
                if string_option_input.lower() in header.name
            ][:10]
        )

    @slash_command(
        name="create_character",
        description=LocalisedDesc(
            **localizer.translations("create_character_description")
        ),
    )
    @slash_option(
        name="name",
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="concept",
        description=LocalisedDesc(**localizer.translations("concept_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="description",
        description=LocalisedDesc(**localizer.translations("description_description")),
        required=False,
        opt_type=OptionType.STRING,
    )
    async def create_character(
        self, ctx: SlashContext, name: str, concept: str, description: str = "..."
    ):
        """Creates a character sheet header."""
        character = CharacterHeader.create(
            str(ctx.author.id), str(ctx.channel.category.id), name, concept, description
        )
        await ctx.send(
            localizer.translate(ctx.locale, "character_created"),
            embed=self.display_character(ctx, character),
        )

    @slash_command(
        name="update_character",
        description=LocalisedDesc(
            **localizer.translations("update_character_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="concept",
        description=LocalisedDesc(**localizer.translations("concept_description")),
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="description",
        description=LocalisedDesc(**localizer.translations("description_description")),
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="image_url",
        description=LocalisedDesc(**localizer.translations("image_url_description")),
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
        character = CharacterHeader.update(
            str(ctx.author.id),
            str(ctx.channel.category.id),
            name,
            concept,
            description,
            image_url,
        )
        await ctx.send(
            localizer.translate(ctx.locale, "character_updated"),
            embed=self.display_character(ctx, character),
        )

    @update_character.autocomplete("name")
    async def update_character_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for updating."""
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="delete_character",
        description=LocalisedDesc(
            **localizer.translations("delete_character_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="confirm",
        description=LocalisedDesc(**localizer.translations("confirm_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    async def delete_character(self, ctx: SlashContext, name: str, confirm: str):
        """Deletes a character sheet header and all entries."""
        if confirm != "confirm":
            await ctx.send(localizer.translate(ctx.locale, "deletion_not_confirmed"))
            return
        CharacterHeader.delete(str(ctx.author_id), str(ctx.channel.category.id), name)
        CharactersheetEntry.delete(
            str(ctx.author_id), str(ctx.channel.category.id), name
        )
        await ctx.send(localizer.translate(ctx.locale, "character_deleted"))

    @delete_character.autocomplete("name")
    async def delete_character_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for deletion."""
        await self.character_name_autocomplete(ctx)

    @slash_command(
        name="show_character",
        description=LocalisedDesc(
            **localizer.translations("show_character_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    async def show_character(self, ctx: SlashContext, name: str):
        """Shows a character sheet header."""
        character = CharacterHeader.get(
            str(ctx.author_id), str(ctx.channel.category.id), name
        )
        await ctx.send(embed=self.display_character(ctx, character))

    @show_character.autocomplete("name")
    async def show_character_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for showing."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        await self.character_name_autocomplete(ctx, True, not settings.character_hidden)

    @slash_command(
        name="add_attribute",
        description=LocalisedDesc(
            **localizer.translations("add_attribute_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_name",
        description=LocalisedDesc(
            **localizer.translations("attribute_name_description")
        ),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_value",
        description=LocalisedDesc(
            **localizer.translations("attribute_value_description")
        ),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_type",
        description=LocalisedDesc(
            **localizer.translations("the_type_of_the_attribute")
        ),
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("attribute")),
                value="attribute",
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("skill")), value="skill"
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("specialty")),
                value="specialty",
            ),
            SlashCommandChoice(
                name=LocalisedName(**localizer.translations("general")), value="general"
            ),
        ],
    )
    @slash_option(
        name="override",
        description=LocalisedDesc(**localizer.translations("override_description")),
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
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        is_gm_current = await is_gm(ctx)
        character_header = CharacterHeader.find_by_name(
            str(ctx.channel.category.id), name
        )[0]
        owner_id = character_header.user_id if is_gm_current else str(ctx.author_id)
        if (
            settings.state == GroupState.CREATING
            or not settings.changes_need_approval
            or await is_gm(ctx)
        ):
            if override:
                CharactersheetEntry.remove_key(
                    owner_id,
                    str(ctx.channel.category.id),
                    name,
                    attribute_name,
                )
            CharactersheetEntry.create(
                owner_id,
                str(ctx.channel.category.id),
                name,
                attribute_name,
                attribute_value,
                AttributeType(attribute_type),
            )
            await ctx.send(localizer.translate(ctx.locale, "attribute_added"))
        else:
            if override:
                SheetModification.delete(
                    str(ctx.author_id),
                    str(ctx.channel.category.id),
                    name,
                    attribute_name,
                )
            SheetModification.create(
                str(ctx.author_id),
                str(ctx.channel.category.id),
                name,
                attribute_name,
                attribute_value,
                AttributeType(attribute_type),
                localizer.translate(ctx.locale, "attribute_added"),
            )
            await ctx.send(
                localizer.translate(
                    ctx.locale, "attribute_added_waiting_for_approval_by_your_gm"
                )
            )

    @add_attribute.autocomplete("name")
    async def add_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for adding attributes."""
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="list_pending_changes",
        description=LocalisedDesc(
            **localizer.translations("list_pending_changes_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    async def list_pending_changes(self, ctx: SlashContext, name: str):
        """Lists pending changes for a character sheet."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
            return
        is_gm_current = await is_gm(ctx)
        if is_gm_current:
            relevant_characters = CharacterHeader.find_by_name(str(ctx.channel.category.id), name)
            for character in relevant_characters:
                changes: dict[str, SheetModification] = {
                    f"{change.sheet_key}": change
                    for change in SheetModification.get(
                        character.user_id, str(ctx.channel.category.id), name
                    )
                    if change.status == ModificationState.PENDING
                }
                if not changes:
                    await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
                    return
                original_character: dict[str, CharactersheetEntry] = {
                    f"{entry.sheet_key}": entry
                    for entry in CharactersheetEntry.get(
                        character.user_id, str(ctx.channel.category.id), name
                    )
                    if entry.sheet_key in changes
                }
        else:
            changes: dict[str, SheetModification] = {
                f"{change.sheet_key}": change
                for change in SheetModification.get(
                    str(ctx.author_id), str(ctx.channel.category.id), name
                )
                if change.status == ModificationState.PENDING
            }
            if not changes:
                await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
                return
            original_character: dict[str, CharactersheetEntry] = {
                f"{entry.sheet_key}": entry
                for entry in CharactersheetEntry.get(
                    str(ctx.author_id), str(ctx.channel.category.id), name
                )
                if entry.sheet_key in changes
            }

        embed = Embed(
            title=localizer.translate(
                ctx.locale, "pending_changes_for_name", name=name
            ),
            color=0xFFFFFF,
        )
        changing_types = {change.attribute_type for change in changes.values()}
        change_lists: dict[AttributeType, list[str]] = {
            attribute_type: [
                f"{change.sheet_key}: {original_character[change.sheet_key].value if change.sheet_key in original_character else '0'} -> {change.value} "
                for change in changes.values()
                if change.attribute_type == attribute_type
            ]
            for attribute_type in changing_types
        }
        for attribute_type, change_list in change_lists.items():
            for i, change_block in enumerate(self.chunk_list(change_list)):
                embed.add_field(name=f"{attribute_type} {i+1}", value=change_block)
        action_advice = (
            localizer.translate(
                ctx.locale,
                "approve_them_all_with_approve_all_changes_or_reject_all_changesnn_or_handle_them_one_by_one_with_approve_change_or_reject_change",
            )
            if is_gm_current
            else localizer.translate(
                ctx.locale,
                "wait_for_your_gm_to_approve_them",
            )
        )
        await ctx.send(action_advice, embed=embed)

    @list_pending_changes.autocomplete("name")
    async def list_pending_changes_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for listing pending changes."""
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="approve_all_changes",
        description=LocalisedDesc(
            **localizer.translations("approve_all_changes_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def approve_all_changes(self, ctx: SlashContext, name: str):
        """Approves all pending changes for a character sheet."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
            return
        character_header = CharacterHeader.find_by_name(str(ctx.channel.category.id), name)[0]
        changes = SheetModification.get(
            character_header.user_id, str(ctx.channel.category.id), name
        )
        change_count = 0
        for change in changes:
            print(change)
            if change.status == ModificationState.PENDING:
                change_count += 1
                CharactersheetEntry.update(
                    str(character_header.user_id),
                    str(ctx.channel.category.id),
                    name,
                    change.sheet_key,
                    change.value,
                    change.attribute_type,
                )
                SheetModification.update(
                    str(character_header.user_id),
                    str(ctx.channel.category.id),
                    name,
                    change.sheet_key,
                    status=ModificationState.APPROVED,
                )
        await ctx.send(
            localizer.translate(
                ctx.locale,
                "all_change_count_changes_approved_for_name",
                change_count=change_count,
                name=name,
            )
        )

    @approve_all_changes.autocomplete("name")
    async def approve_all_changes_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for approving all changes."""
        await self.character_name_autocomplete(ctx, True)

    @slash_command(
        name="reject_all_changes",
        description=LocalisedDesc(
            **localizer.translations("reject_all_changes_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="reason",
        description=LocalisedDesc(**localizer.translations("reason_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def reject_all_changes(self, ctx: SlashContext, name: str, reason: str):
        """Rejects all pending changes for a character sheet."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
            return

        character_header = CharacterHeader.find_by_name(str(ctx.channel.category.id), name)[0]
        changes = SheetModification.get(
            str(character_header.user_id), str(ctx.channel.category.id), name
        )
        change_count = 0
        for change in changes:
            if change.status == ModificationState.PENDING:
                change_count += 1
                SheetModification.update(
                    str(character_header.user_id),
                    str(ctx.channel.category.id),
                    name,
                    change.sheet_key,
                    status=ModificationState.REJECTED,
                    comment=reason,
                )
        await ctx.send(
            localizer.translate(
                ctx.locale,
                "all_change_count_changes_rejected_for_name",
                change_count=change_count,
                name=name,
            )
        )

    @reject_all_changes.autocomplete("name")
    async def reject_all_changes_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for rejecting all changes."""
        await self.character_name_autocomplete(ctx, True)

    async def change_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes attribute names."""
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
        
        character_header = CharacterHeader.find_by_name(str(ctx.channel.category.id), char_name)[0]
        changes = SheetModification.get(
            character_header.user_id, str(ctx.channel.category.id), char_name
        )

        await ctx.send(
            choices=[
                {"name": change.sheet_key, "value": change.sheet_key}
                for change in changes
                if change.status == ModificationState.PENDING
                and ctx.input_text.lower() in change.sheet_key.lower()
            ][:10]
        )

    @slash_command(
        name="approve_change",
        description=LocalisedDesc(
            **localizer.translations("approve_change_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_name",
        autocomplete=True,
        description=LocalisedDesc(
            **localizer.translations("attribute_name_description")
        ),
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def approve_change(self, ctx: SlashContext, name: str, attribute_name: str):
        """Approves a pending change for a character sheet."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
            return
        character_header = CharacterHeader.find_by_name(str(ctx.channel.category.id), name)[0]
        change = SheetModification.get_key(
            character_header.user_id, str(ctx.channel.category.id), name, attribute_name
        )
        if change and change.status == ModificationState.PENDING:
            CharactersheetEntry.update(
                character_header.user_id,
                str(ctx.channel.category.id),
                name,
                change.sheet_key,
                change.value,
                change.attribute_type,
            )
            SheetModification.update(
                character_header.user_id,
                str(ctx.channel.category.id),
                name,
                attribute_name,
                status=ModificationState.APPROVED,
            )
            await ctx.send(
                localizer.translate(ctx.locale, "change_approved_for_name", name=name)
            )
            return
        await ctx.send(localizer.translate(ctx.locale, "no_pending_change_found"))

    @approve_change.autocomplete("name")
    async def approve_change_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for approving changes."""
        await self.character_name_autocomplete(ctx, True)

    @approve_change.autocomplete("attribute_name")
    async def approve_change_attribute_name_autocomplete(
        self, ctx: AutocompleteContext
    ):
        """Autocompletes attribute names for approving changes."""
        self.change_attribute_name_autocomplete(ctx)

    @slash_command(
        name="reject_change",
        description=LocalisedDesc(
            **localizer.translations("reject_change_description")
        ),
    )
    @slash_option(
        name="name",
        autocomplete=True,
        description=LocalisedDesc(**localizer.translations("name_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="attribute_name",
        autocomplete=True,
        description=LocalisedDesc(
            **localizer.translations("attribute_name_description")
        ),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="reason",
        description=LocalisedDesc(**localizer.translations("reason_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def reject_change(
        self, ctx: SlashContext, name: str, attribute_name: str, reason: str
    ):
        """Rejects a pending change for a character sheet."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        if settings.state == GroupState.CREATING or not settings.changes_need_approval:
            await ctx.send(localizer.translate(ctx.locale, "no_pending_changes"))
            return
        character_header = CharacterHeader.find_by_name(str(ctx.channel.category.id), name)[0]
        change = SheetModification.get_key(
            character_header.user_id, str(ctx.channel.category.id), name, attribute_name
        )
        if change and change.status == ModificationState.PENDING:
            SheetModification.update(
                character_header.user_id,
                str(ctx.channel.category.id),
                name,
                attribute_name,
                status=ModificationState.REJECTED,
                comment=reason,
            )
            await ctx.send(
                localizer.translate(ctx.locale, "change_rejected_for_name", name=name)
            )
            return
        await ctx.send(localizer.translate(ctx.locale, "no_pending_change_found"))

    @reject_change.autocomplete("name")
    async def reject_change_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes character names for rejecting changes."""
        await self.character_name_autocomplete(ctx, True)

    @reject_change.autocomplete("attribute_name")
    async def reject_change_attribute_name_autocomplete(self, ctx: AutocompleteContext):
        """Autocompletes attribute names for rejecting changes."""
        self.change_attribute_name_autocomplete(ctx)

    @slash_command(
        name="set_initiative_roll",
    )
    @slash_option(
        name="rule_system",
        description=LocalisedDesc(**localizer.translations("set_initiative_roll_rule_system_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="roll",
        description=LocalisedDesc(**localizer.translations("set_initiative_roll_roll_description")),
        required=True,
        opt_type=OptionType.STRING,
    )
    @check(is_gm)
    async def set_initiative_roll(self, ctx: SlashContext, rule_system: str, roll: str):
        """Sets the initiative roll for the group."""
        RuleSystemRolls.create(rule_system, "INITIATIVE", roll)
        await ctx.send(localizer.translate(ctx.locale, "initiative_roll_set"))

    @slash_command(
        name="gm_roll_initiative",
        description=LocalisedDesc(
            **localizer.translations("gm_roll_initiative_description")
        ),
    )
    @slash_option(
        name="nsc_slots",
        description=LocalisedDesc(**localizer.translations("nsc_slots_description")),
        required=False,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="npc_roll",
        description=LocalisedDesc(**localizer.translations("npc_roll_description")),
        required=False,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="hidden",
        description=LocalisedDesc(**localizer.translations("hidden_description")),
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    @check(is_gm)
    async def gm_roll_initiative(
        self,
        ctx: SlashContext,
        npc_slots: int = 0,
        npc_roll: str = "",
        hidden: bool = False,
    ):
        """Rolls initiative for all players and GMs."""
        settings = CategorySetting.get_by_category(str(ctx.channel.category.id))
        initiative_rule = RuleSystemRolls.get(settings.rule_system, "INITIATIVE")
        if not initiative_rule:
            await ctx.send(
                localizer.translate(
                    ctx.locale,
                    "no_initiative_rule_found_for_settingsrule_system",
                    settingsrule_system=settings.rule_system,
                )
            )
            return
        if npc_slots and not npc_roll:
            await ctx.send(
                localizer.translate(ctx.locale, "please_provide_a_roll_for_the_npcs")
            )
            return

        characters = CharacterHeader.get_by_category(str(ctx.channel.category.id))
        result = localizer.translate(ctx.locale, "initiative_rollsn")
        player_rolls: dict[str, ComplexPool] = {}
        for player_id_char_name, character_list in characters.items():
            player_id, char_name = player_id_char_name
            for character in character_list:
                if character.is_inactive:
                    continue
                sheet_entries: dict[str, int] = {
                    entry.sheet_key: entry.value
                    for entry in CharactersheetEntry.get(
                        player_id, str(ctx.channel.category.id), char_name
                    )
                    if entry.sheet_key in initiative_rule.needed_sheet_values
                }
                if len(sheet_entries) != len(initiative_rule.needed_sheet_values):
                    await ctx.send(
                        localizer.translate(
                            ctx.locale,
                            "missing_values_for_charactername__joininitiative_ruleneeded_sheet_values__setsheet_entrieskeys",
                            charactername=character.name,
                            _joininitiative_ruleneeded_sheet_values__setsheet_entrieskeys=", ".join(
                                set(initiative_rule.needed_sheet_values)
                                - set(sheet_entries.keys())
                            ),
                        )
                    )
                    continue
                player_rolls[char_name] = Parser(
                    initiative_rule.eval(sheet_entries)
                ).build_pool()
        for i in range(npc_slots):
            player_rolls[localizer.translate(ctx.locale, "npc_i1", i1=i + 1)] = Parser(
                npc_roll
            ).build_pool()
        results = [
            (player_name, player_pool.roll().formatted())
            for player_name, player_pool in player_rolls.items()
        ]
        for player_name, player_roll in sorted(
            results, key=lambda x: x[1], reverse=True
        ):
            result += f"{player_name}: {player_roll}\n"
        await ctx.send(result, ephemeral=hidden)
