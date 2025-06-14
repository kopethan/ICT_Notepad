from app.models import Level

def search_levels(session, query):
    return session.query(Level).filter(
        (Level.level_type.ilike(f'%{query}%')) |
        (Level.label.ilike(f'%{query}%')) |
        (Level.timeframe.ilike(f'%{query}%'))
    ).all()
