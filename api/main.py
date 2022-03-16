import sys
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import get_token
from .database import SessionLocal, engine
from .models import User
from .utils.auth import get_current_user, oauth2_scheme

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{username}/companions/", response_model=schemas.Companion)
def create_companion_for_user(username: str, item: schemas.CompanionCreate, db: Session = Depends(get_db)):
    return crud.create_user_companion(db=db, item=item, username=username)


@app.get("/companions/", response_model=List[schemas.Companion])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_companion(db, skip=skip, limit=limit)
    # return items

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post(
    "/companions/event")  # TODO: add response model, schemas.Event, error: `value is not a valid list (type=type_error.list)`
def create_event(companion_id: int, item: schemas.EventCreate, token: str = Depends(oauth2_scheme),
                 db: Session = Depends(get_db)):
    return crud.create_event(db=db, item=item, companion_id=companion_id)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db)):
    return get_token(db=db, form_data=form_data)

print(app.openapi(), file=open('openapi.json', 'w'))
