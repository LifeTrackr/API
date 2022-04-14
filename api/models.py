from datetime import datetime
from datetime import timezone

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from .database import Base
from .schemas import CompanionEvents, CompanionType, PriorityType


class User(Base):
    __tablename__ = "User"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(10))
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
    user_id = Column(Integer, ForeignKey("User.user_id"))


class Event(Base):
    __tablename__ = "Event"
    event_id = Column(Integer, primary_key=True)
    companion_id = Column(Integer, ForeignKey("Companion.companion"))
    user_id = Column(Integer, ForeignKey("User.user_id"))
    user_relationship = relationship("User", foreign_keys=[user_id])
    companion_name = Column(String(10), ForeignKey("Companion.name"))
    companion_relationship = relationship("Companion", foreign_keys=[companion_name])
    companion_type = Column(Enum(CompanionType, name="companion types"), ForeignKey("Companion.companion_type"))
    companion_type_relationship = relationship("Companion", foreign_keys=[companion_type])
    image = Column(String(255), ForeignKey("Companion.image"), default="https://img.icons8.com/ios-glyphs/60/000000"
                                                                       "/dog-heart.png")
    image_relationship = relationship("Companion", foreign_keys=[image])
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
