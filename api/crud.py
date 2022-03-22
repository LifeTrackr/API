from sqlalchemy.orm import Session

from api import models, schemas


def db_add(db, item):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_companion(db: Session, skip: int = 0, limit: int = 100):
    a = db.query(models.Companion).offset(skip).limit(limit).all()
    print(a)
    return a


def create_user_companion(db: Session, item: schemas.CompanionCreate, username: str):
    db_companion = models.Companion(**item.dict(), username_id=username)
    return db_add(db, db_companion)


def create_event(db: Session, item: schemas.EventCreate, companion_id: int):
    db_event = models.Event(**item.dict(), companion_id=companion_id)
    return db_add(db, db_event)
