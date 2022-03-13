from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

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
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    username: str
    is_active: bool
    Companions: List[Companion] = []

    class Config:
        orm_mode = True