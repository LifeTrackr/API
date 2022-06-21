from datetime import datetime
from datetime import timezone

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from .database import Base
from .schemas import CompanionEvents, PriorityType


class User(Base):
    __tablename__ = "User"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(10))
    first_name = Column(String(15))
    last_name = Column(String(25))
    hashed_password = Column(String(64))
    is_active = Column(Boolean)
    companion = relationship("Companion")


class CompanionTypes(Base):
    __tablename__ = "Companion_Types"
    id = Column(Integer, primary_key=True)
    type_name = Column(String)


class Companion(Base):
    __tablename__ = "Companion"
    companion = Column(Integer, primary_key=True)
    name = Column(String(10))
    companion_type = Column(Integer, ForeignKey("Companion_Types.id"))
    notes = Column(String(255))
    image = Column(String(255))
    user_id = Column(Integer, ForeignKey("User.user_id"))


class Event(Base):
    __tablename__ = "Event"
    companion_id = Column(Integer, ForeignKey("Companion.companion"))
    user_id = Column(Integer, ForeignKey("User.user_id"))
    event_id = Column(Integer, primary_key=True)
    name = Column(String(10))
    next_trigger = Column(DateTime)
    qr_code = Column(Integer, default=0)
    notes = Column(String(255))
    priority = Column(Enum(PriorityType, name="priorities"))  # l:low, h:high
    frequency = Column(Interval)
    last_trigger = Column(DateTime, default=datetime.now(timezone.utc))
    action = Column(Enum(CompanionEvents, name="events"))
    update = Column(Boolean)


class EventLogs(Base):
    __tablename__ = "Event_Logs"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("Event.event_id"))
    user_id = Column(Integer, ForeignKey("User.user_id"))
    completed_at = Column(DateTime)
