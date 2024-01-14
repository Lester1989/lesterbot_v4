import asyncio
import os
import pathlib
import sys

sys.path.append(".")

from interactions import Client, Intents, SlashContext, listen, slash_command

bot = Client(intents=Intents.DEFAULT)


@listen()
async def on_ready():
    """This event is called when the bot is ready to respond to commands."""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    print("Guilds:")
    for guild in bot.guilds:
        print(f" - {guild.name} ({guild.id})")


@slash_command(name="my_version", description="My check current bot version")
async def my_version_function(ctx: SlashContext):
    """A slash command that sends the current bot version to the channel."""
    await ctx.send(pathlib.Path("version.txt").read_text(encoding="utf8"))


@slash_command(name="open_todos", description="Return a list of the open Todos")
async def open_todos(ctx: SlashContext):
    """A slash command that sends a "Hello World" message to the channel."""
    await ctx.send(
        """
    - Add logging
    - Add webinterface
    - Add more extensions
      - Scheduler
      - Vampire
      - Hexxen
      - DSA
    - repeatable rolls
"""
    )


if __name__ == "__main__":
    if "DISCORDTOKEN" not in os.environ:
        print("Please set the DISCORDTOKEN environment variable to your bot token")
        exit(1)
    print("Starting bot")
    print("Version: ", pathlib.Path("version.txt").read_text(encoding="utf8"))
    bot.load_extension("exts.polydice")
    bot.load_extension("exts.werewolf_w20")
    bot.load_extension("exts.nsc_gen")
    bot.load_extension("exts.roll_complex")
    bot.load_extension("exts.charsheetmanager")
    print("Loaded extensions")
    bot.start(os.environ.get("DISCORDTOKEN"))
