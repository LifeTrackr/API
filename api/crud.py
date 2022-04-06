from sqlalchemy import delete
from sqlalchemy.orm import Session

from api import models, schemas
from api.database import db_add, modify_session
from api.utils.auth import get_password_hash


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=get_password_hash(user.password), is_active=True)
    return db_add(db, db_user)


def modify_user(db: Session, username: str, new_password: str):
    hashed_password = get_password_hash(new_password)
    db_user = db.query(models.User).filter(models.User.username == username)
    return modify_session(session=db_user, item={"hashed_password": hashed_password}, db=db, by=username)


def get_companions(db: Session, current_user: schemas.User, skip: int = 0, limit: int = 100):
    return db.query(models.Companion).filter(models.Companion.username_id == current_user.username).offset(skip).limit(
        limit).all()


def modify_companion(db: Session, companion_id: int, item: schemas.CompanionCreate):
    db_companion = db.query(models.Companion).filter(models.Companion.companion == companion_id)
    return modify_session(db_companion, item.dict(), db)


def create_user_companion(db: Session, item: schemas.CompanionCreate, username: str):
    db_companion = models.Companion(**item.dict(), username=username)
    return db_add(db, db_companion)


def get_events(db: Session, current_user: schemas.User, skip: int = 0, limit: int = 100):
    db_event = db.query(models.Event).filter(models.Event.username_id == current_user.username)
    return db_event.offset(skip).limit(limit).all()


def create_event(db: Session, item: schemas.EventCreate, companion_id: int, username_id: str, current_time):
    db_event = models.Event(**item.dict(), companion_id=companion_id, username_id=username_id, update=True)
    return db_add(db, db_event)


def modify_event(db: Session, item: schemas.EventBase, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id)
    return modify_session(db_event, item.dict(), db)


def delete_event(db: Session, event_id: int):
    db.execute(delete(models.Event).where(models.Event.companion_id == event_id))
    db.commit()
