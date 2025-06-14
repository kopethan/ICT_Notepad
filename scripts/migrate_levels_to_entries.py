from app.models import Level, LevelEntry, Base
from app.db_utils import get_session
from datetime import datetime

session = get_session()
levels = session.query(Level).all()

for lvl in levels:
    # Only migrate if entry doesn't already exist
    if not lvl.entries:
        entry = LevelEntry(
            level=lvl,
            value=lvl.value,
            note=lvl.notes,
            timestamp=datetime.utcnow()
        )
        session.add(entry)

session.commit()
print("✅ Migration complete: Values moved to LevelEntry")
