import asyncio
import os
import pathlib
from interactions import Client, Intents, listen
from interactions import slash_command, SlashContext
from config import SCOPE_KWARG

bot = Client(intents=Intents.DEFAULT)

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
    A slash command that sends the current bot version to the channel
    """
    await ctx.send(pathlib.Path('version.txt').read_text(encoding='utf8'))


@slash_command(name="open_todos", description="Return a list of the open Todos",**SCOPE_KWARG)
async def my_version_function(ctx: SlashContext):
    """
    A slash command that sends a "Hello World" message to the channel
    """
    await ctx.send('''
    - Make Database persistent
    - Add logging
    - Add webinterface
    - Add more extensions
      - Scheduler
      - Vampire
      - Hexxen
      - DSA
      - CharacterSheet
      - saved rolls
      - gm rolls
    - repeatable rolls
''')


if __name__ == "__main__":
    if "DISCORDTOKEN" not in os.environ:
        print("Please set the DISCORDTOKEN environment variable to your bot token")
        exit(1)
    print("Starting bot")
    print("Version: ",pathlib.Path('version.txt').read_text(encoding='utf8'))
    bot.load_extension("exts.polydice")
    bot.load_extension("exts.werewolf_w20")
    bot.load_extension("exts.nsc_gen")
    print("Loaded extensions")
    bot.start(os.environ.get("DISCORDTOKEN"))
