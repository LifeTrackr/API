from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from .database import Base
from .utils import unpack_types
from datetime import datetime


class User(Base):
    __tablename__ = "User"
    username = Column(String(10), primary_key=True)
    password = Column(String(64))
    is_active = Column(Boolean)
    companion = relationship("Companion")


class Companion(Base):
    __tablename__ = "Companion"
    companion = Column(Integer, primary_key=True)
    name = Column(String(10))
    companion_type = Column(unpack_types.get_companions())
    notes = Column(String(255))
    image = Column(String(255))
    username_id = Column(String(10), ForeignKey("User.username"))


class Event(Base):
    __tablename__ = "Event"
    companion_id = Column(Integer, ForeignKey("Companion.companion"))
    event_id = Column(Integer, primary_key=True)

    name = Column(String(10))
    last_complete = Column(DateTime)
    qr_code = Column(Integer, default=0)
    notes = Column(String(255))
    priority = Column(Enum("l", "m", "h", name="priorities"))  # l:low, h:high
    frequency = Column(DateTime)
    last_trigger = Column(DateTime, default=datetime.now())
    action = Column(unpack_types.get_events())
