"""User database model."""
import uuid
from sqlalchemy import Column, String, Integer
from app.database import Base


def generate_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    tokens = Column(Integer, default=10)
