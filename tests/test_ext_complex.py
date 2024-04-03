import unittest
from interactions import MessageFlags


from app.interactions_unittest import ActionType, SendAction, call_autocomplete, call_slash, call_component, get_client, FakeGuild
from app.exts.roll_complex import RollComplex

class TestCommands(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bot = get_client()
        self.bot.load_extension("app.exts.roll_complex")
        self.fake_guild = FakeGuild(
            client=self.bot,
            channel_names={"welcome": [], "smalltalk": [], "general": []},
            role_names=["admin", "mod", "user"],
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
            'test_ctx_author':self.fake_guild.members[0],
            'test_ctx_author_id':self.fake_guild.members[0].id,
        }
        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        self.bot.unload_extension("app.exts.roll_complex")
        return await super().asyncTearDown()

    async def test_roll_help(self):
        actions = await call_slash(
            RollComplex.roll_help,
            **self.context_kwargs)
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)

    async def test_roll_complex(self):
        actions = await call_slash(
            RollComplex.roll_complex,
            **self.context_kwargs,
            dice_pool="2d6+3")
        self.assertTrue(len(actions) == 2, f"Expected a single action but got {actions}")
        self.assertTrue(actions[0].action_type == ActionType.DEFER, "Expected a defer action")
        self.assertTrue(actions[1].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[1].message["embeds"][0]["description"].startswith("Würfele 2d6+3"), actions[1].message)
        self.assertTrue(len(actions[1].message["components"][0])==2, actions[1].message["components"])
        self.assertTrue(actions[1].message["components"][0]["components"][0]["custom_id"]=="2d6+3", actions[1].message["components"])

    async def test_button_save_complex_pool(self):
        arange_actions = await call_slash(
            RollComplex.roll_complex,
            **self.context_kwargs,
            dice_pool="2d6+3")
        calling_message = arange_actions[1].message
        actions = await call_component(
            RollComplex.button_save_complex_pool,
            **self.context_kwargs,
            test_ctx_custom_id="2d6+3",
            test_ctx_message=calling_message)
        self.assertTrue(len(actions) == 1, f"Expected a single action but got {actions}")
        self.assertTrue(actions[0].action_type == ActionType.SEND_MODAL, "Expected a modal to be sent")
        self.assertTrue(len(actions[0].modal["data"]["components"]) == 3, actions[0].modal["data"]["components"])

    async def test_on_modal_answer(self):
        arange_actions = await call_slash(
            RollComplex.roll_complex,
            **self.context_kwargs,
            dice_pool="2d6+3")
        calling_message = arange_actions[1].message
        arange_actions = await call_component(
            RollComplex.button_save_complex_pool,
            **self.context_kwargs,
            test_ctx_custom_id="2d6+3",
            test_ctx_message=calling_message)
        actions = await call_slash(
            RollComplex.on_modal_answer,
            **self.context_kwargs,
            roll_name="Test",
            dice_pool="2d6+3",
            scope="server",
            )
        self.assertTrue(len(actions) == 1, f"Expected a single action but got {actions}")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        final_actions = await call_slash(
            RollComplex.my_rolls,
            **self.context_kwargs,)
        self.assertTrue(len(final_actions) == 1, f"Expected a single action but got {final_actions}")
        self.assertTrue(final_actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(final_actions[0].message["embeds"][0]["fields"][0]["value"]=="2d6+3", final_actions[0].message)

    async def test_named_roll_with_autocomplete(self):
        arange_actions =await call_slash(
            RollComplex.on_modal_answer,
            **self.context_kwargs,
            roll_name="Test",
            dice_pool="2d6+3",
            scope="server",
        )
        self.assertTrue(len(arange_actions) == 1, f"Expected a single action but got {arange_actions}")
        self.assertTrue(arange_actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        auto_complete_actions = await call_autocomplete(
            RollComplex.roll_name_autocomplete,
            _client=self.bot,
            input_text="Te",
            test_ctx_author_id=self.fake_guild.members[0].id,
            test_ctx_guild_id=self.fake_guild.id,
            test_ctx_channel=self.fake_guild.channels[0],
            test_ctx_channel_id=self.fake_guild.channels[0].id,
        )
        self.assertTrue(len(auto_complete_actions) == 1, f"Expected a single action but got {auto_complete_actions}")
        self.assertTrue(auto_complete_actions[0].action_type == ActionType.SEND_CHOICES, "Expected a choices to be sent")
        self.assertTrue(auto_complete_actions[0].choices[0]["name"]=="Test", auto_complete_actions[0].choices)
        actions = await call_slash(
            RollComplex.named_roll,
            **self.context_kwargs,
            roll_name=auto_complete_actions[0].choices[0]['value'])
        self.assertTrue(len(actions) == 2, f"Expected two actions but got {actions}")
        self.assertTrue(actions[0].action_type == ActionType.DEFER, "Expected a defer action")
        self.assertTrue(actions[1].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[1].message["embeds"][0]["description"].startswith("Würfele 2d6+3"), actions[1].message)
