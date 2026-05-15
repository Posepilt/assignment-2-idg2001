"""Database connection and session setup"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# uses the Docker volume path in production, falls back to a local relative path for testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./olympic.db")
# sqlite doesnt allow multiple threads by default, this turns that off
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Open and close a database session for each request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
