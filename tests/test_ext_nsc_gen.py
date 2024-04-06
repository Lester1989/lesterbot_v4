import unittest
import asyncio
from interactions import MessageFlags


from app.interactions_unittest import ActionType, SendAction, call_slash, get_client, FakeGuild
from app.exts.nsc_gen import NSCGen

class TestCommands(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bot = get_client()
        self.bot.load_extension("app.exts.nsc_gen")
        super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        self.bot.unload_extension("app.exts.nsc_gen")
        super().asyncTearDown()

    async def test_btw_new_default(self):
        actions = await call_slash(
            NSCGen.random_btw_nsc,
            _client=self.bot,
            test_ctx_locale="de",)
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(actions[0].message["embeds"][0]["fields"][0]["name"] == "Spezies",actions[0].message["embeds"][0]["fields"])
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 3, len(actions[0].message["embeds"][0]["fields"]))

    async def test_btw_new_mensch(self):
        actions = await call_slash(
            NSCGen.random_btw_nsc,
            _client=self.bot,
            test_ctx_locale="de",
            mensch=True,)
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(actions[0].message["embeds"][0]["fields"][0]["name"] == "Spezies",actions[0].message["embeds"][0]["fields"])
        self.assertTrue(actions[0].message["embeds"][0]["fields"][0]["value"] == "Mensch",actions[0].message["embeds"][0]["fields"])
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 3, len(actions[0].message["embeds"][0]["fields"]))

    async def test_btw_new_all(self):
        actions = await call_slash(
            NSCGen.random_btw_nsc,
            _client=self.bot,
            test_ctx_locale="de",
            mensch=True,
            zwerg=True,
            elf=True,
            ork=True,
            goblin=True,
            oger=True,
            nymph=True,)
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(actions[0].message["embeds"][0]["fields"][0]["name"] == "Spezies",actions[0].message["embeds"][0]["fields"])
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 3, len(actions[0].message["embeds"][0]["fields"]))

    async def test_btw_new_multiple(self):
        actions = await call_slash(
            NSCGen.random_btw_nsc,
            _client=self.bot,
            test_ctx_locale="de",
            mensch=True,
            zwerg=True,
            elf=True,
            ork=True,
            goblin=True,
            oger=True,
            nymph=True,
            count=3,)
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(actions[0].message["embeds"][0]["fields"][0]["name"] == "Spezies",actions[0].message["embeds"][0]["fields"])
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 4, len(actions[0].message["embeds"][0]["fields"]))
        self.assertTrue(actions[0].message["embeds"][0]["fields"][-1]["name"] == "Beziehungen",actions[0].message["embeds"][0]["fields"])
