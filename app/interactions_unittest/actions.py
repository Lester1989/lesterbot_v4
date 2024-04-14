"""
This module contains the different action classes that can be returned by the interaction functions.
"""

from abc import ABC
from enum import Enum
import time
from typing import Optional


class ActionType(str, Enum):
    """An enumeration of the different action types."""

    DEFER = "defer"
    SEND = "send"
    DELETE = "delete"
    EDIT = "edit"
    CREATE_REACTION = "create_reaction"
    SEND_MODAL = "send_modal"
    SEND_CHOICES = "send_choices"


class BaseAction(ABC):
    """The base action class."""

    action_type: ActionType
    creation_time: float

    def __init__(self):
        self.creation_time = time.time_ns()

    def __repr__(self) -> str:
        return f"{self.action_type} at {self.creation_time}"


class DeferAction(BaseAction):
    """The defer action class with ephemeral attribute."""

    action_type = ActionType.DEFER
    ephemeral: bool

    def __init__(self, ephemeral: bool):
        super().__init__()
        self.ephemeral = ephemeral


class SendAction(BaseAction):
    """The send action class with message attribute."""

    action_type = ActionType.SEND
    message: dict

    def __init__(self, message: dict):
        super().__init__()
        self.message = message

    @property
    def content(self) -> str:
        """The content of the message."""
        return self.message.get("content", "")

    @property
    def embeds(self) -> list[dict]:
        """The embeds of the message."""
        return self.message.get("embeds", [])

    @property
    def components(self) -> list[dict]:
        """The components of the message."""
        return self.message.get("components", [])


class DeleteAction(BaseAction):
    """The delete action class with message_id attribute."""

    action_type = ActionType.DELETE
    message_id: int
    channel_id: Optional[int]
    reason: Optional[str]

    def __init__(
        self,
        message_id: int,
        channel_id: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        super().__init__()
        self.message_id = message_id
        self.channel_id = channel_id
        self.reason = reason


class EditAction(SendAction):
    """The edit action class with message attribute."""

    action_type = ActionType.EDIT
    channel_id: Optional[int]

    def __init__(self, message: dict, channel_id: Optional[int] = None):
        super().__init__(message)
        self.channel_id = channel_id


class CreateReactionAction(BaseAction):
    """The create reaction action class with message_id and emoji attributes."""

    action_type = ActionType.CREATE_REACTION
    message_id: int
    emoji: str
    channel_id: Optional[int]

    def __init__(self, message_id: int, emoji: str, channel_id: Optional[int] = None):
        super().__init__()
        self.message_id = message_id
        self.emoji = emoji
        self.channel_id = channel_id


class SendModalAction(BaseAction):
    """The send modal action class with modal attribute."""

    action_type = ActionType.SEND_MODAL
    modal: dict

    def __init__(self, modal: dict):
        super().__init__()
        self.modal = modal


class SendChoicesAction(BaseAction):
    """The send choices action class with choices attribute."""

    action_type = ActionType.SEND_CHOICES
    choices: list[dict]

    def __init__(self, choices: list[dict]):
        super().__init__()
        self.choices = choices
