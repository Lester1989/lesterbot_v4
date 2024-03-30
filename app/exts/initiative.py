"""This module contains the InitiativeTracker Extension for the Initiative Tracking System."""
from interactions import (
    Embed,
    Extension,
    LocalisedDesc,
    OptionType,
    SlashContext,
    slash_command,
    slash_option,
)

import app.localizer as localizer
from app.library.initiativatracking import (
    InitiativeTracking,
    get_channel_initiative,
    insert_after_name,
    insert_before_index,
    insert_before_name,
    insert_channel_message,
    remove_channel_initiative,
    remove_from_initiative,
    set_channel_initiative,
)


class InitiativeTracker(Extension):
    """An extension for tracking initiative in a channel."""
    async def async_start(self):
        """Print a message when the extension is started."""
        print("Starting InitiativeTracker Extension")

    @slash_command(
        name="initiative_help",
        description=LocalisedDesc(**localizer.translations("initiative_help_description")),
    )
    async def initiative_help(self, ctx: SlashContext):
        """Send a help message for the initiative tracking commands."""
        await ctx.send(
            """
**Initiative Tracking**
You can start a List for initiative by providing a list of ordered participants in the 
**/initiative**
command.
The Participants need to be seperated by comma

Or by inserting a name or two with:
* /initiative_insert_before
* /initiative_insert_after
* /initiative_insert_first
* /initiative_insert_last
You can also use these 4 commands to change the order.

With /initiative_remove you can remove one participant from the list

With /initiative_delete you can delete the complete list

Use /initiative_show to just refresh the message
"""  # TODO: LOCALIZATION FLAG
        )

    @slash_command(
        name="initiative",
        description=LocalisedDesc(**localizer.translations("initiative_description")),
    )
    @slash_option(
        name="participants",
        description=LocalisedDesc(**localizer.translations("participants_description")),
        required=False,
        opt_type=OptionType.STRING,
    )
    async def start_initiative(self, ctx: SlashContext, participants: str = ""):
        """Start a new initiative tracking list."""
        channel_id: str = str(ctx.channel_id)
        if existing_trackings := get_channel_initiative(channel_id):
            if old_message := ctx.channel.get_message(existing_trackings[0].message_id):
                await ctx.channel.delete_message(old_message)
        set_channel_initiative(
            channel_id, *[name.strip() for name in participants.split(",") if name]
        )
        await show_channel_initiative(ctx)

    @slash_command(
        name="initiative_show",
        description=LocalisedDesc(**localizer.translations("initiative_show_description")),
    )
    async def show_initiative(self, ctx: SlashContext):
        """Show the current initiative tracking list."""
        channel_id: str = str(ctx.channel_id)
        trackings = get_channel_initiative(channel_id)
        await ctx.send(embed=render_initiative(ctx, [tracking.name for tracking in trackings]))

    @slash_command(
        name="initiative_insert_before",
        description=LocalisedDesc(**localizer.translations("initiative_insert_before_description")),
    )
    @slash_option(
        name="name",
        description=LocalisedDesc(**localizer.translations("name_description")),
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="name_after",
        description=LocalisedDesc(**localizer.translations("name_after_description")),
        opt_type=OptionType.STRING,
    )
    async def insert_before(self, ctx: SlashContext, name: str, name_after: str):
        """Insert a new entry before the name in the initiative tracking."""
        channel_id: str = str(ctx.channel_id)
        if not get_channel_initiative(channel_id):
            set_channel_initiative(channel_id, name.strip(), name_after.strip())
        else:
            insert_before_name(channel_id, name_after.strip(), name.strip())
        await show_channel_initiative(ctx)

    @slash_command(
        name="initiative_insert_after",
        description=LocalisedDesc(**localizer.translations("initiative_insert_after_description")),
    )
    @slash_option(
        name="name",
        description=LocalisedDesc(**localizer.translations("name_description")),
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="name_before",
        description=LocalisedDesc(**localizer.translations("name_before_description")),
        opt_type=OptionType.STRING,
    )
    async def insert_after(self, ctx: SlashContext, name: str, name_before: str):
        """Insert a new entry after the name in the initiative tracking."""
        channel_id: str = str(ctx.channel_id)
        if not get_channel_initiative(channel_id):
            set_channel_initiative(channel_id, name_before.strip(), name.strip())
        else:
            insert_after_name(channel_id, name_before.strip(), name.strip())
        await show_channel_initiative(ctx)

    @slash_command(
        name="initiative_insert_first",
        description=LocalisedDesc(**localizer.translations("initiative_insert_first_description")),
    )
    @slash_option(
        name="name",
        description=LocalisedDesc(**localizer.translations("name_description")),
        opt_type=OptionType.STRING,
    )
    async def insert_first(self, ctx: SlashContext, name: str):
        """Insert a new entry at the beginning of the initiative tracking."""
        channel_id: str = str(ctx.channel_id)
        if not get_channel_initiative(channel_id):
            set_channel_initiative(channel_id, name.strip())
        else:
            insert_before_index(channel_id, 0, name.strip())
        await show_channel_initiative(ctx)

    @slash_command(
        name="initiative_insert_last",
        description=LocalisedDesc(**localizer.translations("initiative_insert_first_description")),
    )
    @slash_option(
        name="name",
        description=LocalisedDesc(**localizer.translations("name_description")),
        opt_type=OptionType.STRING,
    )
    async def insert_last(self, ctx: SlashContext, name: str):
        """Insert a new entry at the end of the initiative tracking."""
        channel_id: str = str(ctx.channel_id)
        if existing := get_channel_initiative(channel_id):
            insert_before_index(channel_id, existing[-1].initiative_order + 1, name.strip())
        else:
            set_channel_initiative(channel_id, name.strip())
        await show_channel_initiative(ctx)

    @slash_command(
        name="initiative_remove",
        description=LocalisedDesc(**localizer.translations("initiative_remove_description")),
    )
    @slash_option(
        name="name",
        description=LocalisedDesc(**localizer.translations("name_description")),
        opt_type=OptionType.STRING,
    )
    async def remove_name(self, ctx: SlashContext, name: str):
        """Remove a participant from the initiative tracking."""
        channel_id: str = str(ctx.channel_id)
        remove_from_initiative(channel_id, name.strip())
        await show_channel_initiative(ctx, True)

    @slash_command(
        name="initiative_delete",
        description=LocalisedDesc(**localizer.translations("initiative_delete_description")),
    )
    @slash_option(
        name="confirmation",
        description=LocalisedDesc(**localizer.translations("confirmation_description")),
        opt_type=OptionType.STRING,
    )
    async def delete_initiative(self, ctx: SlashContext, confirmation: str):
        """Delete the initiative tracking list."""
        if confirmation != "YES":
            await ctx.send(
                localizer.translate(ctx.locale, "you_need_to_say_yes_all_caps_to_confirm_deletion"),
                ephemeral=True,
            )
            return

        channel_id: str = str(ctx.channel_id)
        if existing_trackings := get_channel_initiative(channel_id):
            if old_message := ctx.channel.get_message(existing_trackings[0].message_id):
                await ctx.channel.delete_message(old_message)
        remove_channel_initiative(channel_id)
        await ctx.send(localizer.translate(ctx.locale, "initiative_removed"))


async def show_channel_initiative(ctx: SlashContext, refresh_message: bool = False):
    """Show the initiative tracking for the channel."""
    channel_id: str = str(ctx.channel_id)
    trackings = get_channel_initiative(channel_id)
    if refresh_message and trackings:
        if old_message := ctx.channel.get_message(trackings[0].message_id):
            await ctx.channel.delete_message(old_message)
            return
    new_message = await ctx.send(embed=render_initiative(ctx, trackings))
    insert_channel_message(channel_id, str(new_message.id))


def render_initiative(ctx: SlashContext, trackings: list[InitiativeTracking]):
    """Render the initiative tracking list as an embed."""
    return Embed(
        title=localizer.translate(ctx.locale, "initiative_tracker"),
        description="\n".join(
            f"{index + 1}. {tracking.name}" for index, tracking in enumerate(trackings)
        )
        if trackings
        else localizer.translate(ctx.locale, "empty__use_insert_commands_to_fill_the_slots"),
    )
