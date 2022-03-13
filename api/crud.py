from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, password=fake_hashed_password, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_companion(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Companion).offset(skip).limit(limit).all()


def create_user_companion(db: Session, item: schemas.CompanionCreate, username: str):
    db_item = models.Companion(**item.dict(), username_id=username)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
