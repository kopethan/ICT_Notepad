from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///db/trading_guide.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
