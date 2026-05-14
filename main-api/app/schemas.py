"""Pydantic schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    tokens: int

    model_config = {"from_attributes": True}


class TokenRedeem(BaseModel):
    user_id: str
    code: str


class OlympicEventCreate(BaseModel):
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
