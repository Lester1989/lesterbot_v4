import asyncio
import os
import pathlib
import sys
from dataclasses import dataclass
from datetime import datetime

sys.path.append(".")

from interactions import (
    Client,
    Intents,
    OptionType,
    SlashContext,
    listen,
    slash_command,
)

bot = Client(intents=Intents.DEFAULT)
build_time = datetime.now()


@dataclass
class PrintableCommand:
    name: str
    description: str


def gather_all_commands(client: Client) -> dict[str, list[PrintableCommand]]:
    """Function for converting list of commands to dict {extension_name: [Command(), ...]}."""
    commands: dict[str, list[PrintableCommand]] = {}
    for command in client.application_commands:
        ext_name = str(command.extension.__class__.__name__)
        if ext_name not in commands:
            commands[ext_name] = []
        commands[ext_name].append(PrintableCommand(command.resolved_name, command.callback.__doc__))
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


"""
Extension: PolyDice
[X] roll_successes
[X] roll_sum

Extension: WerewolfW20
[X] list_gifts_for
[X] show_gift
[X] upload_gifts
[X] ww

Extension: NSCGen
[X] btw_new (not localized)

Extension: RollComplex
[X] roll_complex
[X] named_roll
[X] roll_help
[X] save_roll

Extension: CharSheetManager
[ ] add_attribute
[ ] add_gm
[ ] add_player
[ ] approve_all_changes
[ ] approve_change
[ ] create_character
[ ] creation_finished
[ ] delete_character
[ ] gm_roll_initiative
[ ] list_pending_changes
[ ] reject_all_changes
[ ] reject_change
[ ] remove_player
[ ] resign_gm
[ ] set_rule_system
[ ] show_character
[ ] show_group
[ ] start_group
[ ] update_character

Extension: InitiativeTracker
[ ] initiative_delete
[X] initiative_help
[X] initiative_insert_after
[ ] initiative_insert_before
[ ] initiative_insert_first
[ ] initiative_insert_last
[ ] initiative_remove
[ ] initiative_show
[X] initiative

Extension: NoneType
[ ] my_version
[ ] open_todos
[ ] get_test_list
"""


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
    bot.load_extension("exts.initiative")
    print("Loaded extensions")
    bot.start(os.environ.get("DISCORDTOKEN"))
