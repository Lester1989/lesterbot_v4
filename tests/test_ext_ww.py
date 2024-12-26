import unittest
from unittest.mock import AsyncMock, PropertyMock, patch

from interactions import Attachment

from app.exts.werewolf_w20 import Gift, WerewolfW20
from app.interactions_unittest import (
    ActionType,
    FakeGuild,
    call_autocomplete,
    call_component,
    call_slash,
    get_client,
)
from app.interactions_unittest.helpers import random_snowflake


class TestCommands(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bot = get_client()
        self.bot.load_extension("app.exts.werewolf_w20")
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
            "_client": self.bot,
            "test_ctx_locale": "de",
            "test_ctx_guild": self.fake_guild,
            "test_ctx_channel": self.fake_guild.channels[0],
            'test_ctx_author':self.fake_guild.members[0],
            'test_ctx_author_id':self.fake_guild.members[0].id,
        }
        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_ww_default(self):
        actions = await call_slash(
            WerewolfW20.ww,
            **self.context_kwargs,
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(
            actions[0].message["embeds"][0]["title"]
            == "Würfele 1 Würfel mit Schwierigkeit 6",
            actions[0].message,
        )

    async def test_ww_full(self):
        actions = await call_slash(
            WerewolfW20.ww,
            **self.context_kwargs,
            number=3,
            difficulty=7,
            ones_cancel=False,
            specialty=True,
            spent_willpower=True,
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(
            actions[0].message["embeds"][0]["title"]
            == "Würfele 3 Würfel mit Schwierigkeit 7",
            actions[0].message,
        )

    @patch("app.exts.werewolf_w20.WerewolfW20.download_file", new_callable=AsyncMock)
    async def test_gift_upload(self, download_file_mock: AsyncMock):
        # download_file_mock.return_value = asyncio.Future()
        download_file_mock.return_value = """
[
    {
        "name":"gift1",
        "description_fluff":"fluff1",
        "description_system":"system1",
        "available_for":"cliath"
    },
    {
        "name":"gift2",
        "description_fluff":"fluff2",
        "description_system":"system2",
        "available_for":"ahroun"
    }
]
"""
        actions = await call_slash(
            WerewolfW20.upload_gifts,
            **self.context_kwargs,
            file=Attachment(
                id=random_snowflake(),
                filename="gifts.json",
                size=1000,
                url="http://example.com/gifts.json",
                client=self.bot,
                proxy_url="http://example.com/gifts.json",
            ),
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(
            actions[0].message["content"] == "Hochgeladen 2 Gaben", actions[0].message
        )

        actions = await call_slash(
            WerewolfW20.show_gift, **self.context_kwargs, gift_name="gift1"
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue("embeds" in actions[0].message, actions[0].message)
        self.assertTrue(
            actions[0].message["embeds"][0]["title"] == "gift1", actions[0].message
        )
        self.assertTrue(
            actions[0].message["embeds"][0]["description"] == "fluff1",
            actions[0].message,
        )

        actions = await call_slash(
            WerewolfW20.show_gift, **self.context_kwargs, gift_name="gift5"
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(
            actions[0].message["content"] == "Konnte Gabe gift5 nicht finden",
            actions[0].message,
        )

    async def test_gift_autocomplete(self):
        self.bot.gift_names = ["gift1", "gift2"]
        auto_complete_actions = await call_autocomplete(
            WerewolfW20.gift_name_autocomplete, **self.context_kwargs, input_text="gift"
        )
        self.assertTrue(len(auto_complete_actions) == 1)
        self.assertTrue(auto_complete_actions[0].action_type == ActionType.SEND_CHOICES)
        self.assertTrue(
            auto_complete_actions[0].choices
            == [
                {"name": "gift1", "value": "gift1"},
                {"name": "gift2", "value": "gift2"},
            ],
            auto_complete_actions[0].choices,
        )

    @patch("app.exts.werewolf_w20.WerewolfW20.gifts", new_callable=PropertyMock)
    async def test_list_gifts_for(self, gifts_mock: PropertyMock):
        gifts_mock.return_value = [
            Gift(
                name="Gabe1",
                description_fluff="fluff1",
                description_system="system1",
                available_for="cliath",
            ),
            Gift(
                name="Gabe2",
                description_fluff="fluff2",
                description_system="system2",
                available_for="ahroun",
            ),
        ]
        actions = await call_slash(
            WerewolfW20.list_gifts_for, **self.context_kwargs, auspice="Ahroun"
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(
            actions[0].message["components"][0]["components"][0]["label"] == "Gabe2",
            actions[0].message,
        )
        self.assertTrue(
            actions[0].message["components"][0]["components"][0]["custom_id"]
            == "show_gift_Gabe2",
            actions[0].message,
        )

        actions = await call_component(
            WerewolfW20.show_gift_callback,
            **self.context_kwargs,
            test_ctx_message=actions[0].message,
            test_ctx_custom_id="show_gift_Gabe1",
        )
        self.assertTrue(len(actions) == 1)
        self.assertTrue(actions[0].action_type == ActionType.SEND)
        self.assertTrue(
            actions[0].message["embeds"][0]["title"] == "Gabe1", actions[0].message
        )
        self.assertTrue(
            actions[0].message["embeds"][0]["description"] == "fluff1",
            actions[0].message,
        )
