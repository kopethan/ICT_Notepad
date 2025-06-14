# init_db.py
from app.models import Base
from app import engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Database initialized.")
