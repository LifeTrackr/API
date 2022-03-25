from os import getenv
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uvicorn import run

import api.crud
from api import crud, models, schemas
from api import database
from api.utils import auth
from definitions import get_db

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return api.crud.create_user(db=db, user=user)


@app.post("/users/modify")
def modify_user(new_password: str, db: Session = Depends(get_db),
                current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_user(db=db, username=current_user.username, new_password=new_password)


@app.post("/users/companions/", response_model=schemas.Companion)
def create_companion_for_user(item: schemas.CompanionCreate, db: Session = Depends(get_db),
                              current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_user_companion(db=db, item=item, username=current_user.username)


@app.post("/users/companions/update")
def modify_companion(companion_id: int, item: schemas.CompanionCreate, db: Session = Depends(get_db),
                     current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_companion(db=db, companion_id=companion_id, item=item)


@app.get("/companions/", response_model=List[schemas.Companion])
def read_companions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_companion(db, skip=skip, limit=limit)
    return items


@app.get("/users/token/test")
async def test_token(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/companions/event")
def create_event(companion_id: int, item: schemas.EventCreate, token: str = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):
    return crud.create_event(db=db, item=item, companion_id=companion_id)


@app.post("/companions/event/update")
def modify_event(event_id: int, item: schemas.EventBase, token: str = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):
    return crud.modify_event(db=db, item=item, event_id=event_id)


@app.post("/token", response_model=schemas.Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    return auth.login_for_access_token(form_data=form_data, db=db)


if getenv("PROD") == "FALSE":
    print("WARNING: in production")
    print(app.openapi(), file=open('openapi.json', 'w'))

if __name__ == "__main__":
    reload = getenv("PROD") == "FALSE"
    run("main:app", host="0.0.0.0", port=8000, reload=reload)
