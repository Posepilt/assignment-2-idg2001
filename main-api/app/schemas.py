"""Pydantic schemas for request/response validation"""
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    """Holds the email and password the user submits when creating an account"""
    email: str
    password: str


class UserUpdate(BaseModel):
    """What a user can update on their account"""
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    """What gets sent back to the user after a successful request"""
    id: str
    email: str
    tokens: int

    model_config = {"from_attributes": True}


class TokenRedeem(BaseModel):
    """Holds the user ID and secret code needed to redeem tokens"""
    user_id: str
    code: str


class OlympicEventCreate(BaseModel):
    """Data needed to create a new Olympic event entry. name, noc and sport are required"""
    name: str
    noc: str
    sport: str
    event: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    team: Optional[str] = None
    games: Optional[str] = None
    year: Optional[int] = None
    season: Optional[str] = None
    city: Optional[str] = None
    medal: Optional[str] = None
