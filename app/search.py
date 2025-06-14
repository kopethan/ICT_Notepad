from app.models import Level

def search_levels(session, query):
    from .models import Level
    return session.query(Level).filter(
        (Level.level_type.ilike(f"%{query}%")) | 
        (Level.label.ilike(f"%{query}%")) | 
        (Level.notes.ilike(f"%{query}%"))
    ).all()
