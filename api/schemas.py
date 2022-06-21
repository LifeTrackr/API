from datetime import timedelta, datetime
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
    mist = "mist"
    clean = "clean"


class CompanionType(str, Enum):
    _1 = "dog"
    _2 = "cat"
    _3 = "reptile"
    _4 = "plant"
    _5 = "bird"


class CompanionBase(BaseModel):
    name: str
    companion_type: CompanionType
    notes: str


class CompanionCreate(CompanionBase):
    pass


class Companion(CompanionBase):
    user_id: str
    companion: int

    class Config:
        orm_mode = True


class UploadCompanionImage(BaseModel):
    message: str = "Error Uploading image"
    uploaded: bool = False


class CompanionImageOut(BaseModel):
    companion_id: int
    base64_image: str


class PriorityType(str, Enum):
    l = "l"  # low
    m = "m"  # medium
    h = "h"  # high


class EventBase(BaseModel):
    name: str
    notes: str
    priority: PriorityType
    frequency: timedelta


class EventCreate(EventBase):
    action: CompanionEvents


class Event(EventBase):
    companion_id: int
    event_id: int
    next_trigger: datetime
    qr_code: int
    last_trigger: datetime
    update: bool = False
    user_id: int
    action: CompanionEvents

    class Config:
        orm_mode = True


class EventJoin(Event):
    companion_name: str
    companion_type: str
    # image: str


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    is_active: bool
    user_id: int
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


class CompanionOwnership(BaseModel):
    ownership: bool


class ModifyRow(BaseModel):
    row_id: str = 1
    operation: str
    rows_modified: int = 1


class UpdateUser(ModifyRow):
    table: str = "User"
    operation: str = "update"


class DeleteUser(UpdateUser):
    operation: str = "delete"


class UpdateCompanion(ModifyRow):
    table: str = "Companion"
    operation: str = "update"


class DeleteCompanion(UpdateCompanion):
    operation: str = "delete"


class UpdateEvent(ModifyRow):
    table: str = "Event"
    operation: str = "update"


class DeleteEvent(UpdateEvent):
    operation: str = "delete"


class AuthError(BaseModel):
    detail: str = "Not authenticated"


class ModifyRowError(BaseModel):
    message: str


class ResponseMessage(BaseModel):
    operation: str
    result: bool


class EventTriggered(BaseModel):
    event_id: int
    triggered: bool


class TestBearer(ResponseMessage):
    operation: str = "token for {username} is active and authorized"


class EventLogs(BaseModel):
    event_id: int
    completed_at: datetime
