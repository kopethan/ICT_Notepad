from app.models import PDArray, Level
from sqlalchemy import func

def get_basic_statistics(session):
    total_arrays = session.query(PDArray).count()
    total_levels = session.query(Level).count()

    timeframe_counts = session.query(Level.timeframe, func.count(Level.id)).group_by(Level.timeframe).all()

    return {
        "total_arrays": total_arrays,
        "total_levels": total_levels,
        "timeframe_counts": timeframe_counts
    }

def get_recent_levels(session, limit=10):
    return session.query(Level).order_by(Level.id.desc()).limit(limit).all()
