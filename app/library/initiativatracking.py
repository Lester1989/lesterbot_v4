"""
This module contains classes and functions for initiative tracking in a Discord bot.
It utilizes the sqlmodel library for database operations.
"""
import os
from typing import Optional
from sqlmodel import Field,SQLModel,create_engine,Session,select,delete
connection_string = os.getenv("DB_CONNECTION_STRING", "sqlite:///gifts.db")


engine = create_engine(connection_string, echo=False)

class InitiativeTracking(SQLModel, table=True):
    """
    A class representing an entry in the initiative tracking table.

    Attributes:
    -----------
    id : int
        The unique identifier of the entry.
    initiative_order : int
        The order of the entry in the initiative tracking.
    channel_id : str
        The unique identifier of the channel.
    name : str
        The name of the entry.
    message_id : str
        The unique identifier of the message displaying the initiative tracking.
    """
    id: Optional[int] = Field(default=None, primary_key=True,index=True)
    initiative_order:int
    channel_id:str
    name:str
    message_id:Optional[str]

def shift_order(trackings:list[InitiativeTracking],insert_index:Optional[int]=None,remove_index:Optional[int]=None):
    """
    Shift the initiative order of all entries in the list of trackings.

    Parameters:
    -----------
    trackings : list[InitiativeTracking]
        The list of initiative trackings to shift.
    insert_index : Optional[int]
        The index to insert a new entry at.
    remove_index : Optional[int]
        The index to remove an entry from.
    """
    for entry in trackings:
        if remove_index is not None and entry.initiative_order >= remove_index:
            entry.initiative_order -= 1
        if insert_index is not None and entry.initiative_order >= insert_index:
            entry.initiative_order += 1

def insert_before_index(channel_id:str,index:int,name:str):
    """
    Insert a new entry before the index in the initiative tracking.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    index : int
        The index to insert the new entry before.
    name : str
        The name of the new entry.
    """
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        message_id = current[0].message_id if current else None
        existing_entry:Optional[InitiativeTracking] = next(iter([entry for entry in current if entry.name == name]),None)
        old_index = existing_entry.initiative_order if existing_entry else None
        shift_order(current,index,old_index)
        if existing_entry:
            existing_entry.initiative_order = index
        else:
            session.add(InitiativeTracking(initiative_order=index,channel_id=channel_id,name=name,message_id=message_id))
        session.commit()

def insert_before_name(channel_id:str,name_after:str,name:str):
    """
    Insert a new entry before the name in the initiative tracking.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    name_after : str
        The name to insert the new entry before.
    name : str
        The name of the new entry.
    """
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        message_id = current[0].message_id if current else None
        existing_entry:Optional[InitiativeTracking] = next(iter([entry for entry in current if entry.name == name]),None)
        old_index = existing_entry.initiative_order if existing_entry else None
        index = [entry for entry in current if entry.name == name_after][0].initiative_order
        print('name_after',index)
        print('existing',old_index)
        for entry in current:
            print("before shift",entry.initiative_order,entry.name)
        shift_order(current,index,old_index)
        for entry in current:
            print("after shift",entry.initiative_order,entry.name)
        if existing_entry:
            existing_entry.initiative_order = index
        else:
            session.add(InitiativeTracking(initiative_order=index,channel_id=channel_id,name=name,message_id=message_id))
        session.commit()

def insert_after_name(channel_id:str,name_before:str,name:str):
    """
    Insert a new entry after the name in the initiative tracking.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    name_before : str
        The name to insert the new entry after.
    name : str
        The name of the new entry.
    """
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        message_id = current[0].message_id if current else None
        existing_entry:Optional[InitiativeTracking] = next(iter([entry for entry in current if entry.name == name]),None)
        old_index = existing_entry.initiative_order if existing_entry else None
        index = [entry for entry in current if entry.name == name_before][0].initiative_order+1
        shift_order(current,index,old_index)
        if existing_entry:
            existing_entry.initiative_order = index
        else:
            session.add(InitiativeTracking(initiative_order=index,channel_id=channel_id,name=name,message_id=message_id))
        session.commit()

def set_channel_initiative(channel_id:str,*names:tuple[str], message_id:str=None):
    """
    Set the initiative tracking for a channel.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    *names : tuple[str]
        The names of the entries in the initiative tracking.
    message_id : str
        The unique identifier of the message displaying the initiative tracking.
    """
    with Session(engine) as session:
        session.exec(delete(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id))
        session.commit()
        for i,name in enumerate(names):
            session.add(InitiativeTracking(initiative_order=i,channel_id=channel_id,name=name,message_id=message_id))
        session.commit()

def insert_channel_message(channel_id:str,message_id:str):
    """
    Insert a message ID for a channel's initiative tracking.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    message_id : str
        The unique identifier of the message displaying the initiative tracking.
    """
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        for tracking in current:
            tracking.message_id = message_id
        session.commit()

def remove_from_initiative(channel_id:str,name:str):
    """
    Remove an entry from the initiative tracking.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    name : str
        The name of the entry to remove.
    """
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        existing_entry:Optional[InitiativeTracking] = next(iter([entry for entry in current if entry.name == name]),None)
        old_index = existing_entry.initiative_order if existing_entry else None
        shift_order(current,remove_index=old_index)
        session.exec(delete(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id,InitiativeTracking.name == name))
        session.commit()


def remove_channel_initiative(channel_id:str):
    """
    Remove all entries from the initiative tracking for a channel.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.
    """
    with Session(engine) as session:
        session.exec(delete(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id))
        session.commit()

def get_channel_initiative(channel_id:str):
    """
    Get the initiative tracking for a channel.

    Parameters:
    -----------
    channel_id : str
        The unique identifier of the channel.

    Returns:
    --------
    list[InitiativeTracking]
        The initiative tracking for the channel.
    """
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        return current
