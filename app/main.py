"""
This is a simple bot that demonstrates how to use the interactions library to create a bot that can respond to slash commands.

The bot has a few commands that can be used to interact with it. The commands are defined as functions that are decorated with the `@slash_command` decorator. The `@slash_command` decorator takes the name and description of the command as arguments.

The bot also has an `on_ready` event that is called when the bot is ready to respond to commands. This event is defined as a function that is decorated with the `@listen` decorator.

The bot uses the `Client` class from the interactions library to create a bot client. The `Client` class takes an `intents` argument that specifies the intents that the bot should listen for.

The bot is started by calling the `start` method on the `Client` instance with the bot token as an argument.

The bot also has a `gather_all_commands` function that takes a `Client` instance as an argument and returns a dictionary of all the commands that the bot has defined. The dictionary is of the form `{extension_name: [PrintableCommand(), ...]}` where `PrintableCommand` is a dataclass that represents a command.

The bot also has a `build_time` variable that stores the build time of the bot.

The bot is run by calling the `start` method on the `Client` instance with the bot token as an argument.
"""

import os
import pathlib
import sys
from dataclasses import dataclass
from datetime import datetime
from interactions import (
    Client,
    Intents,
    SlashContext,
    listen,
    slash_command,
)

sys.path.append(".")


bot = Client(intents=Intents.DEFAULT)
build_time = datetime.now()


@dataclass
class PrintableCommand:
    """Dataclass for storing command name and description."""
    name: str
    description: str


def gather_all_commands(client: Client) -> dict[str, list[PrintableCommand]]:
    """Function for converting list of commands to dict {extension_name: [Command(), ...]}."""
    commands: dict[str, list[PrintableCommand]] = {}
    for command in client.application_commands:
        ext_name = str(command.extension.__class__.__name__)
        if ext_name not in commands:
            commands[ext_name] = []
        commands[ext_name].append(
            PrintableCommand(command.resolved_name, command.callback.__doc__)
        )
    return commands


@listen()
async def on_ready():
    """This event is called when the bot is ready to respond to commands."""
    print("Ready", build_time)
    print(f"This bot is owned by {bot.owner}")
    print("Guilds:")
    for guild in bot.guilds:
        print(f" - {guild.name} ({guild.id})")


@slash_command(name="my_version", description="My check current bot version")
async def my_version_function(ctx: SlashContext):
    """A slash command that sends the current bot version to the channel."""
    await ctx.send(
        f'Version {pathlib.Path("version.txt").read_text(encoding="utf8")}\nBuild Time {build_time}'
    )


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
"""
    )


@slash_command(
    name="get_test_list",
    description="Lists all the commands for manual testing",
)
async def get_test_list(ctx: SlashContext):
    """A slash command that sends a list of all commands to the channel."""
    commands = gather_all_commands(bot)
    new_line = "\n  "
    for ext_name, ext_commands in commands.items():
        await ctx.send(
            f'Extension: **{ext_name}**{new_line}{new_line.join([f"{command.name}" for command in ext_commands])}'
        )




if __name__ == "__main__":
    if "DISCORDTOKEN" not in os.environ:
        print("Please set the DISCORDTOKEN environment variable to your bot token")
        sys.exit(1)
    print("Starting bot")
    print("Version: ", pathlib.Path("version.txt").read_text(encoding="utf8"))
    bot.load_extension("exts.polydice")
    bot.load_extension("exts.werewolf_w20")
    bot.load_extension("exts.nsc_gen")
    bot.load_extension("exts.roll_complex")
    bot.load_extension("exts.charsheetmanager")
    bot.load_extension("exts.initiative")
    print("Loaded extensions")
    bot.start(os.environ.get("DISCORDTOKEN"))
