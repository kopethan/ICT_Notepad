from app.models import PDArray, Level
from sqlalchemy import func

def get_basic_statistics(session):
    from .models import PDArray, Level, LevelEntry
    from sqlalchemy import func

    # Total PD Arrays
    total_pd_arrays = session.query(func.count(PDArray.id)).scalar()

    # Total Levels
    total_levels = session.query(func.count(Level.id)).scalar()

    # Total Level Entries
    total_entries = session.query(func.count(LevelEntry.id)).scalar()

    # Levels per PD Array
    levels_per_array = session.query(PDArray.name, func.count(Level.id)).join(Level, PDArray.id == Level.pd_array_id).group_by(PDArray.id).all()

    # Most common Level Type
    level_type_counts = session.query(Level.level_type, func.count(Level.id)).group_by(Level.level_type).order_by(func.count(Level.id).desc()).all()

    return {
        "total_pd_arrays": total_pd_arrays,
        "total_levels": total_levels,
        "total_entries": total_entries,
        "levels_per_array": levels_per_array,
        "level_type_counts": level_type_counts,
    }

def get_recent_levels(session, limit=10):
    return session.query(Level).order_by(Level.id.desc()).limit(limit).all()
