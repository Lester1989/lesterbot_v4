import os

TESTING_GUILDS = [
    int(guild_id) for guild_id in os.environ.get("TESTING_GUILD", "").split(",") if guild_id
] or None
SCOPE_KWARG = {"scopes": TESTING_GUILDS} if TESTING_GUILDS else {}
