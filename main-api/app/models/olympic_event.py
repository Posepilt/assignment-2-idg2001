"""Olympic event database model"""
from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class OlympicEvent(Base):
    """Database model for olympic_events table. Each row is one athlete competing in one event"""
    __tablename__ = "olympic_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    sex = Column(String)
    age = Column(Float)
    height = Column(Float)
    weight = Column(Float)
    team = Column(String)
    noc = Column(String(3), nullable=False)
    games = Column(String)
    year = Column(Integer)
    season = Column(String)
    city = Column(String)
    sport = Column(String, nullable=False)
    event = Column(String)
    medal = Column(String)
