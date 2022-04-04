from datetime import datetime
from datetime import timezone
from os import getenv
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from uvicorn import run

import api.crud
import api.database
from api import crud, models, schemas
from api import database
from api.utils import auth, event_time
from definitions import get_db

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()


@app.get("/users/", response_model=List[schemas.User], tags=["User"], summary="Get all users in database")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/", response_model=schemas.User, tags=["User"], summary="Make a new user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return api.crud.create_user(db=db, user=user)


@app.put("/users/modify/", tags=["User"], summary="Change user password")
def modify_user(new_password: str, db: Session = Depends(get_db),
                current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_user(db=db, username=current_user.username, new_password=new_password)


@app.get("/users/token/test/", tags=["User"], summary="Test Bearer Token")
async def test_token(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/users/companions/", response_model=schemas.Companion, tags=["Companion"], summary="Create a new companion")
def create_companion_for_user(item: schemas.CompanionCreate, db: Session = Depends(get_db),
                              current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_user_companion(db=db, item=item, username=current_user.username)


@app.put("/users/companions/", tags=["Companion"], summary="Modify a companion")
def modify_companion(companion_id: int, item: schemas.CompanionCreate, db: Session = Depends(get_db),
                     current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_companion(db=db, companion_id=companion_id, item=item)


@app.delete("/users/companions/{companion_id}/", tags=["Companion"], summary="Delete a companion")
def delete_companion(companion_id: int, current_user: schemas.User = Depends(auth.get_current_user),
                     db: Session = Depends(get_db), ):
    database.delete_row(db=db, table=models.Event, row=models.Event.companion_id, row_id=companion_id)
    return database.delete_row(db=db, table=models.Companion, row=models.Companion.companion, row_id=companion_id)


@app.get("/companions/", response_model=List[schemas.Companion], tags=["Companion"],
         summary="Get all Companions for user")
def read_companions(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(auth.get_current_user),
                    db: Session = Depends(get_db)):
    return crud.get_companions(db=db, current_user=current_user, skip=skip, limit=limit)


@app.get("/companions/event/", tags=["Event"], summary="Get all events for User")
def get_events(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(auth.get_current_user),
               db: Session = Depends(get_db)):
    return crud.get_events(db=db, current_user=current_user, skip=skip, limit=limit)


@app.post("/companions/event/", tags=["Event"], summary="Create a new event for companion")
def create_event(companion_id: int, item: schemas.EventCreate,
                 current_user: schemas.User = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):
    return crud.create_event(db=db, item=item, companion_id=companion_id, username_id=current_user.username,
                             current_time=datetime.now(timezone.utc))


@app.put("/companions/event/", tags=["Event"], summary="Modify event")
def modify_event(event_id: int, item: schemas.EventBase, current_user: schemas.User = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):
    return crud.modify_event(db=db, item=item, event_id=event_id)


@app.put("/companions/event/last_complete/", tags=["Event"], summary="Complete event",
         description="Update `last_trigger` field to current time ")
def update_last_complete(event_id: int, current_user: schemas.User = Depends(auth.get_current_user),
                         db: Session = Depends(get_db)):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id)
    item = {"update": True}
    return crud.modify_session(session=db_event, item=item, db=db)


@app.get("/companions/event/triggered/{event_id}/", tags=["Event"], summary="Check if event is triggered")
def is_event_triggered(event_id: int, current_user: schemas.User = Depends(auth.get_current_user),
                       db: Session = Depends(get_db)):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    db_time = db.query(func.now()).first()
    for d in db_time:
        time = d
    return {"event_id": event_id,
            "triggered": event_time.check_trigger(delta=db_event.frequency, db_time=time,
                                                  last_trigger=db_event.last_trigger)}


@app.delete("/companions/event/{event_id}/", tags=["Event"], summary="Delete event")
def delete_event(event_id: int, token: str = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return database.delete_row(db=db, table=models.Event, row=models.Event.event_id, row_id=event_id)


@app.post("/token/", response_model=schemas.Token, tags=["Authentication"], summary="Login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    return auth.login_for_access_token(form_data=form_data, db=db)


if getenv("PROD") == "FALSE":
    print("WARNING: in production")
    print(app.openapi(), file=open('openapi.json', 'w'))

if __name__ == "__main__":
    reload = getenv("PROD") == "FALSE"
    run("main:app", host="0.0.0.0", port=8000, reload=reload)
