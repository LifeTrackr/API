from datetime import datetime
from os import getenv
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uvicorn import run

import api.crud
import api.database
from api import crud, models, schemas
from api import database
from api.utils import auth
from definitions import get_db

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
print("hello")


@app.get("/users/", response_model=List[schemas.User], tags=["User"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/users/", response_model=schemas.User, tags=["User"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return api.crud.create_user(db=db, user=user)


@app.put("/users/modify", tags=["User"])
def modify_user(new_password: str, db: Session = Depends(get_db),
                current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_user(db=db, username=current_user.username, new_password=new_password)


@app.get("/users/token/test", tags=["User"])
async def test_token(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/users/companions/", response_model=schemas.Companion, tags=["Companion"])
def create_companion_for_user(item: schemas.CompanionCreate, db: Session = Depends(get_db),
                              current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_user_companion(db=db, item=item, username=current_user.username)


@app.put("/users/companions/", tags=["Companion"])
def modify_companion(companion_id: int, item: schemas.CompanionCreate, db: Session = Depends(get_db),
                     current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_companion(db=db, companion_id=companion_id, item=item)


@app.delete("/users/companions/{companion_id}", tags=["Companion"])
def delete_companion(companion_id: int, current_user: schemas.User = Depends(auth.get_current_user),
                     db: Session = Depends(get_db), ):
    database.delete_row(db=db, table=models.Event, row=models.Event.companion_id, row_id=companion_id)
    return database.delete_row(db=db, table=models.Companion, row=models.Companion.companion, row_id=companion_id)


@app.get("/companions/", response_model=List[schemas.Companion], tags=["Companion"])
def read_companions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.get_companions(db=db, current_user=current_user, skip=skip, limit=limit)


# @app.get("/companions/event/", tags=["Event"])
# def get_events(db: Session = Depends(get_db), current_user:)


@app.post("/companions/event/", tags=["Event"])
def create_event(companion_id: int, item: schemas.EventCreate,
                 current_user: schemas.User = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):
    return crud.create_event(db=db, item=item, companion_id=companion_id, username_id=current_user.username)


@app.put("/companions/event/", tags=["Event"])
def modify_event(event_id: int, item: schemas.EventBase, current_user: schemas.User = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):
    return crud.modify_event(db=db, item=item, event_id=event_id)


@app.put("/companions/event/last_complete", tags=["Event"])
def update_last_complete(event_id: int, current_user: schemas.User = Depends(auth.get_current_user),
                         db: Session = Depends(get_db)):
    e = models.Event()
    e.last_complete = datetime.now()
    return crud.modify_event(db=db, item=e, event_id=event_id)


@app.delete("/companions/event/{event_id}", tags=["Event"])
def delete_event(event_id: int, token: str = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return database.delete_row(db=db, table=models.Event, row=models.Event.event_id, row_id=event_id)


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    return auth.login_for_access_token(form_data=form_data, db=db)


if getenv("PROD") == "FALSE":
    print("WARNING: in production")
    print(app.openapi(), file=open('openapi.json', 'w'))

if __name__ == "__main__":
    reload = getenv("PROD") == "FALSE"
    run("main:app", host="0.0.0.0", port=8000, reload=reload)
