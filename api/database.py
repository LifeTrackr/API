import os

import sqlalchemy.exc
from dotenv import load_dotenv
from sqlalchemy import create_engine, engine, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from api import models

load_dotenv()
try:
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]
    production = os.getenv("PROD")
except KeyError:
    raise KeyError("Error: Missing env file")
host_args = db_host.split(":")
if len(host_args) == 1:
    db_hostname, db_port = db_host, os.environ["DB_PORT"]
elif len(host_args) == 2:
    db_hostname, db_port = host_args[0], int(host_args[1])
else:
    raise KeyError("Error: Host args > 2")

try:
    db_url = os.environ.get('DATABASE_URL')
    print(db_url)

    engine = create_engine(db_url)
except Exception:
    engine = create_engine(engine.url.URL.create(drivername="postgresql+psycopg2", username=db_user, password=db_pass,
                                                 host=db_hostname, port=db_port, database=db_name))

def db_add(db: Session, item):
    db.add(item)
    try:
        db.commit()
    except sqlalchemy.exc.DataError as e:
        msg = {"error": "Database validation error"}
        if production:
            msg["db_msg"] = e.statement
        return msg
    db.refresh(item)
    return item


def modify_session(session, item, db: Session):
    try:
        session.update(item)
    except sqlalchemy.exc.DataError as e:
        msg = {"error": "Database validation error"}
        if production:
            msg["db_msg"] = e.statement
        return msg
    db.commit()
    return {"modified": True}


def delete_row(db: Session, table: models, row: models, row_id: int):
    stmt = delete(table).where(row == row_id)
    try:
        db.execute(stmt)
        db.commit()
    except sqlalchemy.exc.DataError as e:
        msg = {"error": "Database validation error"}
        if production:
            msg["db_msg"] = e.statement
        return msg
    return {"deleted": True}


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
