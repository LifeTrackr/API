from datetime import datetime
from datetime import timezone

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from .database import Base
from .schemas import CompanionEvents, CompanionType, PriorityType


class User(Base):
    __tablename__ = "User"
    username = Column(String(10), primary_key=True)
    hashed_password = Column(String(64))
    is_active = Column(Boolean)
    companion = relationship("Companion")


class Companion(Base):
    __tablename__ = "Companion"
    companion = Column(Integer, primary_key=True)
    name = Column(String(10))
    companion_type = Column(Enum(CompanionType, name="companion types"))
    notes = Column(String(255))
    image = Column(String(255))
    username_id = Column(String(10), ForeignKey("User.username"))


class Event(Base):
    __tablename__ = "Event"
    companion_id = Column(Integer, ForeignKey("Companion.companion"))
    username_id = Column(String(10), ForeignKey("User.username"))
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
