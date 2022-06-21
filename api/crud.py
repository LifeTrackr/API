from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.orm import Session

from api import models, schemas
from api.database import db_add, modify_row
from api.utils import s3_interface, auth
from api.utils.auth import get_password_hash


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, first_name=user.first_name, last_name=user.last_name,
                          hashed_password=get_password_hash(user.password), is_active=True)
    return db_add(db=db, item=db_user)


def modify_user(db: Session, user_id: int, new_password: str):
    hash_pw = get_password_hash(new_password)
    stmt = update(models.User).where(models.User.user_id == user_id).values(hashed_password=hash_pw)
    return modify_row(stmt=stmt, _id=user_id, table=models.User, db=db)


def get_companions(db: Session, current_user: schemas.User):
    j = select(models.Companion, models.CompanionTypes) \
        .join(models.CompanionTypes, models.CompanionTypes.id == models.Companion.companion_type) \
        .filter(models.Companion.user_id == current_user.user_id)
    result = db.execute(j).all()
    r = []
    for row in result:
        companion_data = row._data[0]
        companion_type_data = row._data[1]
        r.append({
            "name": companion_data.name,
            "companion_type": companion_type_data.type_name,
            "notes": companion_data.notes,
            "user_id": companion_data.user_id,
            "companion": companion_data.companion,
        })
    return r


def modify_companion(db: Session, companion_id: int, item: schemas.CompanionCreate):
    item.companion_type = int(item.companion_type.name[1:])
    stmt = update(models.Companion).where(models.Companion.companion == companion_id).values(**item.dict())
    return modify_row(stmt=stmt, _id=companion_id, table=models.Companion, db=db)


def create_user_companion(db: Session, item: schemas.CompanionCreate, user_id: int):
    db_companion = models.Companion(name=item.name, notes=item.notes, user_id=user_id,
                                    companion_type=int(item.companion_type.name[1:]))
    return db_add(db, db_companion)


def _data_from_event_query(result):
    return [{
        "name": row._data[0].name,
        "notes": row._data[0].notes,
        "priority": row._data[0].priority,
        "frequency": row._data[0].frequency,
        "companion_id": row._data[0].companion_id,
        "event_id": row._data[0].event_id,
        "next_trigger": row._data[0].next_trigger,
        "qr_code": row._data[0].qr_code,
        "last_trigger": row._data[0].last_trigger,
        "update": row._data[0].update,
        "user_id": row._data[0].user_id,
        "action": row._data[0].action,
        "companion_name": row._data[1].name,
        "companion_type": row._data[2].type_name
    } for row in result]


def get_events_query(current_user: schemas.User, event_id: int = -1):
    if event_id >= 0:
        return select(models.Event, models.Companion, models.CompanionTypes) \
            .join(models.Companion, models.Companion.companion == models.Event.companion_id) \
            .join(models.CompanionTypes) \
            .filter(models.Event.user_id == current_user.user_id).filter(models.Event.event_id == event_id)
    return select(models.Event, models.Companion, models.CompanionTypes) \
        .join(models.Companion, models.Companion.companion == models.Event.companion_id) \
        .join(models.CompanionTypes) \
        .filter(models.Event.user_id == current_user.user_id)


def get_events(db: Session, current_user: schemas.User):
    result = db.execute(get_events_query(current_user)).all()
    return _data_from_event_query(result)


def get_event(db: Session, current_user: schemas.User, event_id):
    result = db.execute(get_events_query(current_user, event_id)).all()
    return _data_from_event_query(result)[0]


def create_event(db: Session, item: schemas.EventCreate, companion_id: int, username_id: int):
    db_event = models.Event(**item.dict(), companion_id=companion_id, user_id=username_id, update=True)
    return db_add(db, db_event)


def modify_event(db: Session, item: schemas.EventBase, event_id: int):
    stmt = (update(models.Event).where(models.Event.event_id == event_id).values(**item.dict()))
    return modify_row(stmt=stmt, _id=event_id, table=models.Event, db=db)


def get_event_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    db_logs = db.query(models.EventLogs).filter(models.EventLogs.user_id == user_id)
    return db_logs.offset(skip).limit(limit).all()


def get_companion_image(companion_id: int, db: Session, current_user: schemas.User):
    rows = get_companions(db=db, current_user=current_user)
    for row in rows:
        if row.companion == companion_id:
            return {"companion_id": companion_id, "base64_image": s3_interface.get_image(row.companion)}
    raise HTTPException(status_code=404, detail="Companion not found")


def get_all_companion_images(db: Session, current_user: schemas.User):
    rows = get_companions(db=db, current_user=current_user)
    result = []
    for row in rows:
        result.append({"companion_id": row.companion, "base64_image": s3_interface.get_image(row.companion)})
    return result


def companion_ownership(companion_id: int, token: str, db: Session):
    q = db.query(models.Companion).filter(models.Companion.companion == companion_id).all()
    if q and auth.test_token(token=token, db=db):
        return q[0].companion == companion_id
    return False
