import unittest
import asyncio
from interactions import MessageFlags
from interactions.client.errors import CommandCheckFailure


from app.interactions_unittest import ActionType, SendAction, call_slash, get_client, FakeGuild,call_autocomplete
from app.exts.charsheetmanager import CharSheetManager

class TestCommands(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bot = get_client()
        self.bot.load_extension("app.exts.charsheetmanager")
        self.fake_guild = FakeGuild(
            client=self.bot,
            channel_names={"table1": ["charactermanagement"], "smalltalk": [], "general": []},
            role_names=["admin", "gm", "user"],
            member_names={
                "user1": ["user", "admin"],
                "user2": ["user"],
                "user3": ["user"],
            },
        )
        self.context_kwargs = {
            '_client':self.bot,
            'test_ctx_locale':"de",
            'test_ctx_guild':self.fake_guild,
            'test_ctx_channel':self.fake_guild.channels[0],

        }
        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        self.bot.unload_extension("app.exts.charsheetmanager")
        return await super().asyncTearDown()

    async def test_full_creation(self):
        channel_charactermanagement = next(channel for channel in self.fake_guild.channels if channel.name == "charactermanagement")
        special_context_kwargs = self.context_kwargs | {
            'test_ctx_channel': channel_charactermanagement,
            'test_ctx_author': self.fake_guild.members[0]
            }
        print("starting")
        actions = await call_slash(
            CharSheetManager.start_group,
            **special_context_kwargs,
            rule_system="sw ffg")
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["title"] == "Gruppe table1 (wird erstellt)", actions[0].message)

        print("adding players")
        actions = await call_slash(
            CharSheetManager.add_player,
            **special_context_kwargs,
            player=self.fake_guild.members[1])
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["title"] == "Gruppe table1 (wird erstellt)", actions[0].message)
        self.assertTrue( "user2" in actions[0].message["embeds"][0]["fields"][3]["value"], actions[0].message)

        actions = await call_slash(
            CharSheetManager.add_player,
            **special_context_kwargs,
            player=self.fake_guild.members[2])
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["title"] == "Gruppe table1 (wird erstellt)", actions[0].message)
        self.assertTrue( "user3" in actions[0].message["embeds"][0]["fields"][3]["value"], actions[0].message)

        print("creating character")
        special_context_kwargs['test_ctx_author'] = self.fake_guild.members[1]
        actions = await call_slash(
            CharSheetManager.create_character,
            **special_context_kwargs,
            name="char2",
            concept="concept2",
            )
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["title"] == "char2", actions[0].message)
        self.assertTrue(actions[0].message["embeds"][0]["description"] == "concept2", actions[0].message)
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 2, actions[0].message)

        auto_complete_actions = await call_autocomplete(
            CharSheetManager.character_name_autocomplete,
            **special_context_kwargs,
            input_text="ch")
        self.assertTrue(len(auto_complete_actions) == 1, "Expected a single action")
        self.assertTrue(auto_complete_actions[0].action_type == ActionType.SEND_CHOICES, "Expected a choices to be sent")
        self.assertTrue(len(auto_complete_actions[0].choices) == 1, auto_complete_actions[0].choices)
        self.assertTrue(auto_complete_actions[0].choices[0]["name"] == "char2", auto_complete_actions[0].choices)

        print("modify character")
        actions = await call_slash(
            CharSheetManager.add_attribute,
            **special_context_kwargs,
            name="char2",
            attribute_name="attribute1",
            attribute_value="5",
            attribute_type="general")
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")

        print("show character")
        actions = await call_slash(
            CharSheetManager.show_character,
            **special_context_kwargs,
            name="char2",)
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["title"] == "char2", actions[0].message)
        self.assertTrue(actions[0].message["embeds"][0]["description"] == "concept2", actions[0].message)
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 3, actions[0].message)
        self.assertTrue("attribute1" in actions[0].message["embeds"][0]["fields"][2]["value"], actions[0].message)

        print("check no changes")
        actions = await call_slash(
            CharSheetManager.list_pending_changes,
            **special_context_kwargs,
            name="char2",
            )
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["content"] == "Keine ausstehenden Änderungen", actions[0].message)

        print("create second character")
        special_context_kwargs['test_ctx_author'] = self.fake_guild.members[2]
        actions = await call_slash(
            CharSheetManager.create_character,
            **special_context_kwargs,
            name="char3",
            concept="concept3",
            )
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["title"] == "char3", actions[0].message)
        self.assertTrue(actions[0].message["embeds"][0]["description"] == "concept3", actions[0].message)
        self.assertTrue(len(actions[0].message["embeds"][0]["fields"]) == 2, actions[0].message)

        print("finish group creation")
        with self.assertRaises(CommandCheckFailure,msg="Should only be allowed for GM"):
            await call_slash(
                CharSheetManager.creation_finished,
                **special_context_kwargs,
            )

        special_context_kwargs['test_ctx_author'] = self.fake_guild.members[0]
        actions = await call_slash(
            CharSheetManager.creation_finished,
            **special_context_kwargs,
            )
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["content"] == "Erstellung beendet", actions[0].message)
        self.assertTrue("user2 (char2)" in actions[0].message["embeds"][0]["fields"][2]["value"], actions[0].message["embeds"][0]["fields"])

        print("make change")
        special_context_kwargs['test_ctx_author'] = self.fake_guild.members[1]
        actions = await call_slash(
            CharSheetManager.add_attribute,
            **special_context_kwargs,
            name="char2",
            attribute_name="attribute2",
            attribute_value="5",
            attribute_type="general")
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue("wartet auf Genehmigung" in actions[0].message["content"], actions[0].message)

        print("check changes")
        special_context_kwargs['test_ctx_author'] = self.fake_guild.members[0]
        actions = await call_slash(
            CharSheetManager.list_pending_changes,
            **special_context_kwargs,
            name="char2",
            )
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue("attribute2" in actions[0].message["embeds"][0]["fields"][0]["value"], actions[0].message)
        # self.assertTrue(False, actions[0].message)

        print("approve changes")
        actions = await call_slash(
            CharSheetManager.approve_all_changes,
            **special_context_kwargs,
            name="char2",
            )
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["content"] == "Alle 1 Änderungen genehmigt für char2", actions[0].message)


