"""This module contains the InitiativeTracker Extension for the Initiative Tracking System."""
from interactions import (
    Embed,
    Extension,
    LocalisedDesc,
    OptionType,
    SlashContext,
    slash_command,
    slash_option,
    AllowedMentions,
)

from app import localizer


class XCard(Extension):
    """Safetytool."""
    async def async_start(self):
        """Print a message when the extension is started."""
        print("Starting XCard Extension")

    @slash_command(
        name="x",
        description=LocalisedDesc(**localizer.translations("x_card_quick")),
    )
    async def initiative_help(self, ctx: SlashContext):
        '''X Card'''
        await ctx.send(
            """
            **X Card**
            """,
            ephemeral=True
        )
        mentions = ' '.join(member.mention for member in ctx.channel.members)
        await ctx.channel.send(
            f"""```
+-----------------+
| X             X |
|  X           X  |
|   X         X   |
|    X       X    |
|     X     X     |
|      X   X      |
|       X X       |
|        X        |
|       X X       |
|      X   X      |
|     X     X     |
|    X       X    |
|   X         X   |
|  X           X  |
| X   X Card    X |
+-----------------+
```
{mentions}
            """,
            allowed_mentions=AllowedMentions.all(),
            delete_after=300
        )
