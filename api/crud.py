from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from api import models, schemas
from api.database import db_add, modify_row
from api.utils.auth import get_password_hash


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=get_password_hash(user.password), is_active=True)
    return db_add(db, db_user)


def modify_user(db: Session, username: str, new_password: str):
    hash_pw = get_password_hash(new_password)
    stmt = (update(models.User).values({"hashed_password": hash_pw}).where(models.User.username == username))
    return modify_row(stmt=stmt, _id=username, table=models.User, db=db)


def get_companions(db: Session, current_user: schemas.User, skip: int = 0, limit: int = 100):
    return db.query(models.Companion).filter(models.Companion.user_id == current_user.user_id).offset(skip).limit(
        limit).all()


def modify_companion(db: Session, companion_id: int, item: schemas.CompanionCreate):
    stmt = (update(models.Companion).values(**item.dict()).where(models.Companion.companion == companion_id))

    return modify_row(stmt=stmt, _id=companion_id, table=models.Companion, db=db)


def create_user_companion(db: Session, item: schemas.CompanionCreate, user_id: int):
    db_companion = models.Companion(**item.dict(), user_id=user_id)
    return db_add(db, db_companion)


def get_events(db: Session, current_user: schemas.User, skip: int = 0, limit: int = 100):
    db_event = db.query(models.Event).filter(models.Event.user_id == current_user.user_id)
    return db_event.offset(skip).limit(limit).all()


def create_event(db: Session, item: schemas.EventCreate, companion_id: int, username_id: int):
    db_event = models.Event(**item.dict(), companion_id=companion_id, user_id=username_id, update=True)
    return db_add(db, db_event)


def modify_event(db: Session, item: schemas.EventBase, event_id: int):
    stmt = (update(models.Event).values(**item.dict()).where(models.Event.event_id == event_id))
    return modify_row(stmt=stmt, _id=event_id, table=models.Event, db=db)


def delete_event(db: Session, event_id: int):
    db.execute(delete(models.Event).where(models.Event.companion_id == event_id))
    db.commit()
