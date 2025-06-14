from app.models import Level
# app/level.py

from .models import Level
from sqlalchemy.orm import Session

from .models import LevelEntry
from datetime import datetime

def add_level(session, pd_array_id, level_type, value, timeframe, label, notes):
    from .models import Level
    new_level = Level(
        pd_array_id=pd_array_id,
        level_type=level_type,
        value=value,
        timeframe=timeframe,
        label=label,
        notes=notes
    )
    session.add(new_level)
    session.commit()
    return new_level

def add_level_entry(session, level_id, value, note=""):
    entry = LevelEntry(
        level_id=level_id,
        value=value,
        note=note,
        timestamp=datetime.utcnow()
    )
    session.add(entry)
    session.commit()
    return entry

def list_levels(session, pd_array_id):
    return session.query(Level).filter(Level.pd_array_id == pd_array_id).all()

def list_levels_by_pd_array_id(session: Session, pd_array_id: int):
    return session.query(Level).filter_by(pd_array_id=pd_array_id).order_by(Level.label).all()

def edit_level(session, level_id, level_type=None, value=None, timeframe=None, label=None, notes=None):
    level = session.query(Level).get(level_id)
    if level:
        if level_type: level.level_type = level_type
        if value: level.value = value
        if timeframe: level.timeframe = timeframe
        if label: level.label = label
        if notes is not None: level.notes = notes
        session.commit()
    return level

def delete_level(session, level_id):
    level = session.query(Level).get(level_id)
    if level:
        session.delete(level)
        session.commit()
    return level

def delete_levels_by_type(session, pd_array_id, level_type_to_delete):
    levels_to_delete = session.query(Level).filter(
        Level.pd_array_id == pd_array_id,
        Level.level_type == level_type_to_delete
    ).all()

    count = len(levels_to_delete)

    for lvl in levels_to_delete:
        session.delete(lvl)

    session.commit()

    return count

def get_latest_level_entry(session, level_id):
    return session.query(LevelEntry).filter_by(level_id=level_id).order_by(LevelEntry.timestamp.desc()).first()
