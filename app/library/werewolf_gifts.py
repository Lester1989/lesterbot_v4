'''
This module contains the database model for gifts in the werewolf game.
'''
import json
import os
from sqlalchemy import create_engine,  Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy.orm import sessionmaker

# create engine
engine = create_engine(os.getenv('DB_CONNECTION_STRING', 'sqlite:///gifts.db'), echo=False)

Session = sessionmaker(bind=engine,expire_on_commit=False)

class Base(DeclarativeBase):
    """
    A base class for all database models.
    """



class Gift(Base):
    """
    A class representing a gift in the werewolf game.

    Attributes:
    -----------
    id : int
        The unique identifier of the gift.
    name : str
        The name of the gift.
    description_fluff : str
        A description of the gift in a more narrative style.
    description_system : str
        A description of the gift in a more technical style.
    available_for : str
        A string representing which roles can receive the gift.
    """
    __tablename__ = 'gifts'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String)
    description_fluff:Mapped[str] = mapped_column(String)
    description_system:Mapped[str] = mapped_column(String)
    available_for:Mapped[str] = mapped_column(String)

def load_gifts() -> list[Gift]:
    """
    Load all gifts from the database.

    Returns:
    --------
    list[Gift]
        A list of all gifts in the database.
    """
    with Session() as session:
        return session.query(Gift).all()

def parse_json(json_string:str) -> list[Gift]:
    """
    Parse a JSON string and add the gifts to the database.

    Parameters:
    -----------
    json_string : str
        A JSON string representing a list of gifts.

    Returns:
    --------
    list[Gift]
        A list of all gifts parsed from the JSON string.
    """
    if json_list := json.loads(json_string):
        gift_list = [Gift(**json_dict) for json_dict in json_list]
        print(len(gift_list), "gifts loaded from JSON file")
        with Session() as session:
            session.add_all(gift_list)
            session.commit()
        return gift_list
    return []
