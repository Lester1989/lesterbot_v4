import asyncio
import os
import pathlib
from interactions import Client, Intents, listen
from interactions import slash_command, SlashContext

bot = Client(intents=Intents.DEFAULT)
TESTING_GUILDS = [int(guild_id) for guild_id in os.environ.get("TESTING_GUILD","").split(",") if guild_id] or None
SCOPE_KWARG = {"scopes": TESTING_GUILDS} if TESTING_GUILDS else {}
@listen()
async def on_ready():
    """
    This event is called when the bot is ready to respond to commands
    """
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    print("Guilds:")
    for guild in bot.guilds:
        print(f" - {guild.name} ({guild.id})")

@slash_command(name="my_version", description="My check current bot version",**SCOPE_KWARG)
async def my_version_function(ctx: SlashContext):
    """
    A slash command that sends a "Hello World" message to the channel
    """
    await ctx.send(pathlib.Path('version.txt').read_text(encoding='utf8'))


if __name__ == "__main__":
    if "DISCORDTOKEN" not in os.environ:
        print("Please set the DISCORDTOKEN environment variable to your bot token")
        exit(1)
    print("Starting bot")
    print("Version: ",pathlib.Path('version.txt').read_text(encoding='utf8'))
    bot.load_extension("exts.polydice")
    print("Loaded extensions")
    bot.start(os.environ.get("DISCORDTOKEN"))
