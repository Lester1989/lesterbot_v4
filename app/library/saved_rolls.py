""" This file contains the model for saved rolls and the functions to interact with the database."""
import os
from functools import lru_cache
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

connection_string = os.getenv("DB_CONNECTION_STRING", "sqlite:///gifts.db")


engine = create_engine(connection_string, echo=True)


class SavedRoll(SQLModel, table=True):
    """
    A class representing a saved roll in the database.

    Attributes:
    -----------
    id : int
        The unique identifier of the saved roll.
    user_id : str
        The unique identifier of the user who saved the roll.
    discord_id : str
        The unique identifier of the Discord entity the roll is saved for.
    scope : str
        The scope of the saved roll (server, category, or channel).
    name : str
        The name of the saved roll.
    dice_pool : str
        The dice pool of the saved roll.
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: str
    discord_id: str
    scope: str
    name: str
    dice_pool: str

    def is_available(self, server_id: str, category_id: str, channel_id: str) -> bool:
        """
        Check if the saved roll is available for the given Discord entity.

        Parameters:
        -----------
        server_id : str
            The unique identifier of the server.
        category_id : str
            The unique identifier of the category.
        channel_id : str
            The unique identifier of the channel.

        Returns:
        --------
        bool
            True if the saved roll is available for the given Discord entity, False otherwise.
        """
        return (
            self.scope == "server"
            and self.discord_id == server_id
            or self.scope == "category"
            and self.discord_id == category_id
            or self.scope == "channel"
            and self.discord_id == channel_id
        )

@lru_cache()
def get_by_user(user_id: str) -> list[SavedRoll]:
    """
    Get all saved rolls for a user.

    Parameters:
    -----------
    user_id : str
        The unique identifier of the user.

    Returns:
    --------
    list[SavedRoll]
        A list of all saved rolls for the user.
    """
    with Session(engine) as session:
        return list(session.exec(select(SavedRoll).where(SavedRoll.user_id == user_id)))


@lru_cache()
def get_by_id(saved_id: int):
    """
    Get a saved roll by its unique identifier.

    Parameters:
    -----------
    saved_id : int
        The unique identifier of the saved roll.

    Returns:
    --------
    Optional[SavedRoll]
        The saved roll with the given unique identifier, or None if no such saved roll exists.
    """
    with Session(engine) as session:
        return session.get(SavedRoll, saved_id)


def invalidate_cache():
    """ Invalidate the cache for the get_by_user function. """
    get_by_user.cache_clear()
