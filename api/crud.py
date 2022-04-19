from sqlalchemy import update, text
from sqlalchemy.orm import Session

from api import models, schemas
from api.database import db_add, modify_row
from api.utils.auth import get_password_hash


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=get_password_hash(user.password), is_active=True)
    return db_add(db=db, item=db_user)


def modify_user(db: Session, user_id: int, new_password: str):
    hash_pw = get_password_hash(new_password)
    stmt = update(models.User).where(models.User.user_id == user_id).values(hashed_password=hash_pw)
    return modify_row(stmt=stmt, _id=user_id, table=models.User, db=db)


def get_companions(db: Session, current_user: schemas.User, skip: int = 0, limit: int = 100):
    return db.query(models.Companion).filter(models.Companion.user_id == current_user.user_id).offset(skip).limit(
        limit).all()


def modify_companion(db: Session, companion_id: int, item: schemas.CompanionCreate):
    stmt = update(models.Companion).where(models.Companion.companion == companion_id).values(**item.dict())
    return modify_row(stmt=stmt, _id=companion_id, table=models.Companion, db=db)


def create_user_companion(db: Session, item: schemas.CompanionCreate, user_id: int):
    db_companion = models.Companion(**item.dict(), user_id=user_id)
    return db_add(db, db_companion)


def get_events(db: Session, current_user: schemas.User, skip: int = 0, limit: int = 100):
    #    db_event = db.query(models.event_view)
    #     q = db.query(models.Event).join(models.Companion, models.Event.companion_id == models.Companion.companion)
    stmt = text("""SELECT
  "Event".companion_id,
  "Event".user_id,
  "Event".name as name,
  "Event".event_id,
  "Event".notes,
  qr_code,
  priority,
  frequency,
  last_trigger,
  next_trigger,
  action,
  "Companion".name as companion_name,
  companion_type,
  image
FROM "Event"
INNER JOIN "Companion" on "Companion".companion = "Event".companion_id;""")
    result = db.execute(stmt).all()
    r = []
    for row in result:
        #     # companion_id, user_id, eventname, qr_code, priority, frequency, last_trigger, next_trigger, action,
        #     #        companionname, companion_type, image
        r.append(row._mapping)
    return r


def create_event(db: Session, item: schemas.EventCreate, companion_id: int, username_id: int):
    companion = db.query(models.Companion).where(models.Companion.companion == companion_id).first()
    db_event = models.Event(**item.dict(), companion_id=companion_id, user_id=username_id, update=True,
                            companion_name=companion.name, companion_type=companion.companion_type,
                            image=companion.image)
    return db_add(db, db_event)


def modify_event(db: Session, item: schemas.EventBase, event_id: int):
    stmt = (update(models.Event).where(models.Event.event_id == event_id).values(**item.dict()))
    return modify_row(stmt=stmt, _id=event_id, table=models.Event, db=db)


def get_event_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    db_logs = db.query(models.EventLogs).filter(models.EventLogs.user_id == user_id)
    return db_logs.offset(skip).limit(limit).all()
