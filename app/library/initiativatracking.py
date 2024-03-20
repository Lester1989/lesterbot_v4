import os 
from sqlmodel import Field,SQLModel,create_engine,Session,select,delete
from typing import Optional
from functools import lru_cache
connection_string = os.getenv("DB_CONNECTION_STRING", "sqlite:///gifts.db")


engine = create_engine(connection_string, echo=True)

class InitiativeTracking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True,index=True)
    initiative_order:int
    channel_id:str
    name:str
    message_id:Optional[str]

def shift_order(trackings:list[InitiativeTracking],insert_index:Optional[int]=None,remove_index:Optional[int]=None):
    for entry in trackings:
        if remove_index and entry.initiative_order > remove_index:
            entry.initiative_order -= 1
        if insert_index and entry.initiative_order >= insert_index:
            entry.initiative_order += 1

def insert_before_index(channel_id:str,index:int,name:str):
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
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        message_id = current[0].message_id if current else None
        existing_entry:Optional[InitiativeTracking] = next(iter([entry for entry in current if entry.name == name]),None)
        old_index = existing_entry.initiative_order if existing_entry else None
        index = [entry for entry in current if entry.name == name_after][0].initiative_order
        shift_order(current,index,old_index)
        if existing_entry:
            existing_entry.initiative_order = index
        else:
            session.add(InitiativeTracking(initiative_order=index,channel_id=channel_id,name=name,message_id=message_id))
        session.commit()

def insert_after_name(channel_id:str,name_before:str,name:str):
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
    with Session(engine) as session:
        session.exec(delete(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id))
        session.commit()
        for i,name in enumerate(names):
            session.add(InitiativeTracking(initiative_order=i,channel_id=channel_id,name=name,message_id=message_id))
        session.commit()

def insert_channel_message(channel_id:str,message_id:str):
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        for tracking in current:
            tracking.message_id = message_id
        session.commit()

def remove_from_initiative(channel_id:str,name:str):
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        existing_entry:Optional[InitiativeTracking] = next(iter([entry for entry in current if entry.name == name]),None)
        old_index = existing_entry.initiative_order if existing_entry else None
        shift_order(current,remove_index=old_index)
        session.exec(delete(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id,InitiativeTracking.name == name))
        session.commit()


def remove_channel_initiative(channel_id:str):
    with Session(engine) as session:
        session.exec(delete(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id))
        session.commit()

def get_channel_initiative(channel_id:str):
    with Session(engine) as session:
        current:list[InitiativeTracking] = list(session.exec(select(InitiativeTracking).where(InitiativeTracking.channel_id == channel_id).order_by(InitiativeTracking.initiative_order)))
        return current
    


            