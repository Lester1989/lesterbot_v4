import unittest
import asyncio
from interactions import MessageFlags


from app.interactions_unittest import ActionType, SendAction, call_slash, get_client, FakeGuild
from app.exts.initiative import InitiativeTracker

class TestCommands(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bot = get_client()
        self.bot.load_extension("app.exts.initiative")
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
        }
        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        self.bot.unload_extension("app.exts.initiative")
        return await super().asyncTearDown()

    async def test_initiative_help(self):
        actions = await call_slash(
            InitiativeTracker.initiative_help,
            _client=self.bot)
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)

    async def test_initiative(self):
        actions = await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        self.assertTrue(len(actions) == 1, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. a","2. b", "3. c"], actions[0].message)
        actions = await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="x,y,z")
        self.assertTrue(len(actions) == 2, "Expected a single action")
        self.assertTrue(actions[0].action_type == ActionType.DELETE, "Expected a message to be deleted")
        self.assertTrue(actions[1].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[1].message["embeds"][0]["description"].split("\n") == ["1. x","2. y", "3. z"], actions[1].message)

    async def test_initiative_insert_before(self):
        await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        actions = await call_slash(
            InitiativeTracker.insert_before,
            **self.context_kwargs,
            name="x",
            name_after="b")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. a","2. x","3. b","4. c"], actions[0].message)
        actions = await call_slash(
            InitiativeTracker.insert_before,
            **self.context_kwargs,
            name="z",
            name_after="a")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. z","2. a","3. x","4. b","5. c"], actions[0].message)

    async def test_initiative_remove(self):
        arange_actions =await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        first_action:SendAction = arange_actions[0]
        self.assertTrue(first_action.message["id"]  in self.bot._fake_cache, f'{first_action.message["id"]} not in {self.bot._fake_cache}')
        actions = await call_slash(
            InitiativeTracker.remove_name,
            **self.context_kwargs,
            name="b")
        self.assertTrue(len(actions) == 2, f"Expected a delete and send action got {actions}")
        for action in actions:
            print(action.creation_time, action.action_type,)
        self.assertTrue(actions[0].action_type == ActionType.DELETE, f"Expected a message to be deleted {actions}")
        self.assertTrue(actions[1].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[1].message["embeds"][0]["description"].split("\n") == ["1. a","2. c"], actions[1].message)

    async def test_initiative_delete(self):
        arange_actions =await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        first_action:SendAction = arange_actions[0]
        self.assertTrue(first_action.message["id"]  in self.bot._fake_cache, f'{first_action.message["id"]} not in {self.bot._fake_cache}')
        actions = await call_slash(
            InitiativeTracker.delete_initiative,
            **self.context_kwargs,
            confirmation="yes")
        self.assertTrue(len(actions) == 1, f"Expected a delete and send action got {actions}")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message['flags'] & MessageFlags.EPHEMERAL, actions[0].message['flags'])
        actions = await call_slash(
            InitiativeTracker.delete_initiative,
            **self.context_kwargs,
            confirmation="YES")
        self.assertTrue(len(actions) == 2, f"Expected a delete and send action got {actions}")
        self.assertTrue(actions[0].action_type == ActionType.DELETE, "Expected a message to be deleted")
        self.assertTrue(actions[1].action_type == ActionType.SEND, "Expected a message to be sent")

    async def test_initiative_insert_last(self):
        await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        actions = await call_slash(
            InitiativeTracker.insert_last,
            **self.context_kwargs,
            name="x")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. a","2. b","3. c","4. x"], actions[0].message)

    async def test_initiative_insert_first(self):
        await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        actions = await call_slash(
            InitiativeTracker.insert_first,
            **self.context_kwargs,
            name="x")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. x","2. a","3. b","4. c"], actions[0].message)

    async def test_initiative_insert_after(self):
        await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        actions = await call_slash(
            InitiativeTracker.insert_after,
            **self.context_kwargs,
            name="x",
            name_before="b")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. a","2. b","3. x","4. c"], actions[0].message)
        actions = await call_slash(
            InitiativeTracker.insert_after,
            **self.context_kwargs,
            name="z",
            name_before="a")
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. a","2. z","3. b","4. x","5. c"], actions[0].message)

    async def test_initiative_show(self):
        await call_slash(
            InitiativeTracker.start_initiative,
            **self.context_kwargs,
            participants="a,b,c")
        actions = await call_slash(
            InitiativeTracker.show_initiative,
            **self.context_kwargs)
        self.assertTrue(actions[0].action_type == ActionType.SEND, "Expected a message to be sent")
        self.assertTrue(actions[0].message["embeds"][0]["description"].split("\n") == ["1. a","2. b","3. c"], actions[0].message)
