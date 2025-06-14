# app/models.py

from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Association table
pd_array_tag_table = Table(
    'pd_array_tag', Base.metadata,
    Column('pd_array_id', Integer, ForeignKey('pd_arrays.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    pd_arrays = relationship(
        "PDArray",
        secondary=pd_array_tag_table,
        back_populates="tags"
    )

class PDArray(Base):
    __tablename__ = 'pd_arrays'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    session = Column(String)
    date = Column(Date)
    notes = Column(Text)
    color = Column(String, nullable=True)
    timeframes = Column(String)  # Store comma-separated timeframes like "1m, 5m, 15m"

    levels = relationship("Level", back_populates="pd_array", cascade="all, delete-orphan")
    tags = relationship(
        "Tag",
        secondary=pd_array_tag_table,
        back_populates="pd_arrays"
    )

class Level(Base):
    __tablename__ = 'levels'

    id = Column(Integer, primary_key=True)
    pd_array_id = Column(Integer, ForeignKey('pd_arrays.id'))
    level_type = Column(String)
    value = Column(String)  # We use String → can store "1.2345" or "10:30"
    label = Column(String)
    notes = Column(Text)

    pd_array = relationship("PDArray", back_populates="levels")
    entries = relationship("LevelEntry", back_populates="level", cascade="all, delete-orphan")
     
class LevelEntry(Base):
    __tablename__ = 'level_entries'

    id = Column(Integer, primary_key=True)
    level_id = Column(Integer, ForeignKey('levels.id'))
    value = Column(String)
    note = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    level = relationship("Level", back_populates="entries")

class AppSetting(Base):
    __tablename__ = 'app_settings'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(String)
