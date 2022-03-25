from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class CompanionEvents(str, Enum):
    water = "water"
    fertilize = "fertilize"
    repot = "repot"
    feed = "feed"
    walk = "walk"
    groom = "groom"
    play = "play"
    # feed_ = "feed"
    mist = "mist"
    clean = "clean"


class CompanionType(str, Enum):
    plant = "plant"
    dog = "dog"
    cat = "cat"
    reptile = "reptile"


class CompanionBase(BaseModel):
    name: str
    companion_type: CompanionType
    notes: str
    image: str


class CompanionCreate(CompanionBase):
    pass


class Companion(CompanionBase):
    username_id: str
    companion: int

    class Config:
        orm_mode = True


class PriorityType(str, Enum):
    l = "l"  # low
    m = "m"  # medium
    h = "h"  # high


class EventBase(BaseModel):
    name: str
    notes: str
    priority: PriorityType
    frequency: datetime


class EventCreate(EventBase):
    action: CompanionEvents


class Event(EventBase):
    companion_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    hashed_password: str
    is_active: bool
    Companions: List[Companion] = []

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: Optional[str] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
