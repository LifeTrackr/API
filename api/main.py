import base64
import io
from os import getenv
from typing import List

from PIL import Image
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, update, delete
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from uvicorn import run

import api.crud
import api.database
from api import crud, models, schemas
from api import database
from api.utils import auth, s3_interface, cache
from api.utils.s3_interface import upload_image
from get_dbs import get_db, get_autocommit_db

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()
companion_cache = cache.CompanionTypeCache(database.SessionLocal)


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


@app.put("/users/modify/", tags=["User"], response_model=schemas.UpdateUser, summary="Change user password",
         responses={401: {"model": schemas.AuthError}})
def modify_user(new_password: str, db: Session = Depends(get_db),
                current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_user(db=db, user_id=current_user.user_id, new_password=new_password)


@app.get("/users/token/test/", tags=["User"], response_model=schemas.TestBearer, summary="Test Bearer Token",
         responses={401: {"model": schemas.AuthError}})
def test_token(current_user: schemas.User = Depends(auth.get_current_user)):
    return {"operation": f"token for {current_user.username} is active and authorized",
            "result": current_user.is_active}


@app.post("/users/companions/", response_model=schemas.Companion, tags=["Companion"], summary="Create a new companion",
          responses={401: {"model": schemas.AuthError}})
def create_companion_for_user(item: schemas.CompanionCreate, db: Session = Depends(get_db),
                              current_user: schemas.User = Depends(auth.get_current_user)):
    result = crud.create_user_companion(db=db, item=item, user_id=current_user.user_id)
    if type(result) == models.Companion:
        result.companion_type = companion_cache[result.companion_type]  # hack to map companion type id to a name
    return result


@app.post("/users/companions/upload_image/{companion_id}", tags=["Companion"], summary="Upload image for companion ",
          response_model=schemas.UploadCompanionImage)
async def upload_companion_image(companion_id: int, file: UploadFile = File(...)):
    contents = await file.read()
    file_validated = s3_interface.validate_image(contents, file)
    if file_validated:
        try:
            with Image.open(io.BytesIO(contents)) as im:
                await file.close()
                im = im.resize((128, 128))
                im.convert("RGB")
                buffered = io.BytesIO()
                im.save(buffered, format="png")
                img_str = base64.b64encode(buffered.getvalue())
                upload_image(img_str, companion_id)
                return {"message": f"Uploaded image to companion {companion_id}", "uploaded": True}
        except OSError as e:
            print(e)
    else:
        await file.close()
        return {"message:": file_validated}


@app.get("/companions/image/{companion_id}", response_model=schemas.CompanionImageOut, summary="Get Companion image",
         responses={401: {"model": schemas.AuthError}, 404: {"description": "The item was not found"}},
         tags=["Companion"])
async def get_companion_image(companion_id: int, db: Session = Depends(get_db),
                              current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.get_companion_image(companion_id=companion_id, db=db, current_user=current_user)


@app.get("/companions/images/{companion_id}", response_model=List[schemas.CompanionImageOut], tags=["Companion"],
         summary="Get All companion images by user", responses={401: {"model": schemas.AuthError},
                                                                404: {"description": "The item was not found"}})
async def get_companion_image(db: Session = Depends(get_db),
                              current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.get_all_companion_images(db=db, current_user=current_user)


@app.put("/users/companions/", response_model=schemas.UpdateCompanion, tags=["Companion"], summary="Modify a companion",
         responses={403: {"model": schemas.ModifyRowError, "description": "Database validation error"},
                    401: {"model": schemas.AuthError}})
def modify_companion(companion_id: int, item: schemas.CompanionCreate, db: Session = Depends(get_autocommit_db),
                     _: schemas.User = Depends(auth.get_current_user)):
    return crud.modify_companion(db=db, companion_id=companion_id, item=item)


@app.delete("/users/companions/{companion_id}/", tags=["Companion"], summary="Delete a companion",
            responses={401: {"model": schemas.AuthError}}, response_model=schemas.DeleteCompanion)
def delete_companion(companion_id: int, _: schemas.User = Depends(auth.get_current_user),
                     db: Session = Depends(get_autocommit_db)):
    stmt = (delete(models.Companion).where(models.Companion.companion == companion_id))
    return database.modify_row(stmt=stmt, _id=companion_id, table=models.Companion, db=db)


@app.get("/companions/", response_model=List[schemas.Companion], summary="Get all Companions for user",
         responses={401: {"model": schemas.AuthError}}, tags=["Companion"])
def read_companions(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.get_companions(db=db, current_user=current_user)


@app.get("/companions/event/", response_model=List[schemas.EventJoin], tags=["Event"],
         summary="Get all events for User",
         responses={401: {"model": schemas.AuthError}})
def get_events(current_user: schemas.User = Depends(auth.get_current_user),
               db: Session = Depends(get_autocommit_db)):
    return crud.get_events(db=db, current_user=current_user)


@app.post("/companions/event/", tags=["Event"], response_model=schemas.EventJoin,
          summary="Create a new `event` for `companion`", responses={401: {"model": schemas.AuthError}})
def create_event(companion_id: int, item: schemas.EventCreate, db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(auth.get_current_user)):
    event_id = crud.create_event(db=db, item=item, companion_id=companion_id, username_id=current_user.user_id).event_id
    return crud.get_event(db=db, current_user=current_user, event_id=event_id)


@app.put("/companions/event/", tags=["Event"], response_model=schemas.UpdateEvent, summary="Modify event",
         responses={401: {"model": schemas.AuthError}})
def modify_event(event_id: int, item: schemas.EventBase, _: schemas.User = Depends(auth.get_current_user),
                 db: Session = Depends(get_autocommit_db)):
    return crud.modify_event(db=db, item=item, event_id=event_id)


@app.put("/companions/event/last_complete/{event_id}/", tags=["Event"], summary="Complete event",
         description="Update `last_trigger` field to current time", responses={401: {"model": schemas.AuthError}},
         response_model=schemas.UpdateEvent)
def update_last_complete(event_id: int, _: schemas.User = Depends(auth.get_current_user),
                         db: Session = Depends(get_autocommit_db)):
    stmt = (update(models.Event).values({"update": True}).where(models.Event.event_id == event_id))
    return crud.modify_row(stmt=stmt, _id=event_id, table=models.Event, db=db)


@app.get("/companions/event/triggered/{event_id}/", response_model=schemas.EventTriggered, tags=["Event"],
         summary="Check if event is triggered", responses={401: {"model": schemas.AuthError},
                                                           422: {"model": schemas.ModifyRowError}})
def is_event_triggered(event_id: int, _: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    if db_event is None:
        return JSONResponse(status_code=422, content={"message": "Invalid ID"})
    db_time = db.query(func.now()).first()
    for db_time in db_time:
        return {"event_id": event_id, "triggered": db_time > (db_event.last_trigger + db_event.frequency)}


@app.get("/companions/event/triggered/{user_id}/", tags=["Event"], summary="Check all event per user is triggered",
         responses={401: {"model": schemas.AuthError}})
def all_event_triggered(user_id: str, _: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    pass


@app.delete("/companions/event/{event_id}/", tags=["Event"], summary="Delete event", response_model=schemas.DeleteEvent,
            responses={401: {"model": schemas.AuthError}})
def delete_event(event_id: int, _: str = Depends(auth.get_current_user), db: Session = Depends(get_autocommit_db)):
    stmt = (delete(models.Event).where(models.Event.event_id == event_id))
    return database.modify_row(db=db, table=models.Event, stmt=stmt, _id=event_id)


@app.get("/companions/event/logs/", tags=["Event"], response_model=List[schemas.EventLogs])
def get_event_logs(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db),
                   skip: int = 0, limit: int = 100):
    return crud.get_event_logs(db=db, user_id=current_user.user_id, skip=skip, limit=limit)


@app.post("/token/", response_model=schemas.Token, tags=["Authentication"], summary="Login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    return auth.login_for_access_token(form_data=form_data, db=db)


@app.post("/token/companion_ownership", response_model=schemas.CompanionOwnership, tags=["Authentication"],
          summary="Test access token for companion ownership")
def companion_ownership(companion_id: int, token: str, db: Session = Depends(get_db)):
    return {"ownership": crud.companion_ownership(db=db, token=token, companion_id=companion_id)}


if getenv("PROD") == "FALSE":
    print(app.openapi(), file=open('openapi.json', 'w'))
else:
    print("WARNING: in production")

if __name__ == "__main__":
    reload = getenv("PROD") == "FALSE"
    run("main:app", host="0.0.0.0", port=8001, reload=reload)
