# app/db_utils.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

def init_db(db_path='db/trading_guide.db'):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
