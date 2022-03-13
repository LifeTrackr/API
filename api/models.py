from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from enum import Enum
from .database import Base


class CompanionType(Enum):
    pl = "plant"
    cd = "cat / dog"
    re = "reptile"

class User(Base):
    __tablename__ = "User"
    username = Column(String(10), primary_key=True)
    password = Column(String(64))
    is_active = Column(Boolean)
    companion = relationship("Companion")

class Companion(Base):
    __tablename__ = "Companion"
    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    companion_type = Column(String(2), Enum(CompanionType))
    notes = Column(String(255))
    image = Column(String(255))
    username_id = Column(String(10), ForeignKey("User.username"))

class Event(Base):
    __tablename__ = "Event"
    event_id = Column(Integer, primary_key=True)
    name = Column(String(10))
    last_complete = Column(DateTime)
    qr_code = Column(Integer)
    notes = Column(String(255))
    priority = Column(Integer)
    frequency = Column(DateTime)
    last_trigger = Column(DateTime)
    companion_id = Column(Integer, ForeignKey("Companion.id"))

