import os
from functools import lru_cache
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

connection_string = os.getenv("DB_CONNECTION_STRING", "sqlite:///gifts.db")


engine = create_engine(connection_string, echo=True)


class SavedRoll(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: str
    discord_id: str
    scope: str
    name: str
    dice_pool: str

    def is_available(self, server_id: str, category_id: str, channel_id: str) -> bool:
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
    with Session(engine) as session:
        return list(session.exec(select(SavedRoll).where(SavedRoll.user_id == user_id)))


@lru_cache()
def get_by_id(id: int):
    with Session(engine) as session:
        return session.get(SavedRoll, id)


def invalidate_cache():
    get_by_user.cache_clear()
