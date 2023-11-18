import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# create engine
engine = create_engine(os.getenv("DB_CONNECTION_STRING", "sqlite:///gifts.db"), echo=False)

Session = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """A base class for all database models."""
