from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas
from .models import User
from .utils.auth import hash_password


def db_add(db, item):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, password=fake_hashed_password, is_active=True)
    return db_add(db, db_user)


def get_companion(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Companion).offset(skip).limit(limit).all()


def create_user_companion(db: Session, item: schemas.CompanionCreate, username: str):
    db_companion = models.Companion(**item.dict(), username_id=username)
    return db_add(db, db_companion)


def create_event(db: Session, item: schemas.EventCreate, companion_id: int):
    db_event = models.Event(**item.dict(), companion_id=companion_id)
    a = db_add(db, db_event)
    print(a)
    return a


def get_token(db: Session, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = hash_password(form_data.password)
    print(hashed_password, user.hashed_password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail=" Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}
