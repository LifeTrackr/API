from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class CompanionType(str, Enum):
    pl = "plant"
    cd = "cat / dog"
    re = "reptile"

class CompanionBase(BaseModel):
    name: str
    companion_type: CompanionType
    notes: str
    image: str

class CompanionCreate(CompanionBase):
    pass

class Companion(CompanionBase):
    id: int
    username_id: str
    class Config:
        orm_mode = True