import os

import sqlalchemy.exc
from dotenv import load_dotenv
from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.responses import JSONResponse

load_dotenv()
try:
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]
    production = True if os.getenv("PROD") is True else False
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
    if not db_url:
        db_url = os.environ.get('CONNECTION_STRING')
    engine = create_engine(db_url.replace('postgres://', 'postgresql://'))
except Exception as e:
    print(e)
    engine = create_engine(engine.url.URL.create(drivername="postgresql+psycopg2", username=db_user, password=db_pass,
                                                 host=db_hostname, port=db_port, database=db_name))


def db_add(db: Session, item):
    db.add(item)
    try:
        db.commit()
    except Exception as e:
        msg = {"error": "Database validation error"}
        if not production:
            msg["db_msg"] = e.args[0]

    db.refresh(item)
    return item


def get_op(stmt):
    if stmt.is_update:
        return "update"
    if stmt.is_delete:
        return "delete"
    return "Unknown"


def modify_row(stmt, _id, table, db: Session):
    try:
        result = db.execute(stmt)
    except sqlalchemy.exc.DataError as e:
        message = {"error": "Database validation error"}
        if not production:
            message["db_msg"] = e.statement
        return JSONResponse(
            status_code=403,
            content=message,
        )
    return {"table": table.__tablename__, "row_id": str(_id),
            "operation": get_op(stmt), "rows_modified": result.rowcount}


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocalAutocommit = sessionmaker(autocommit=True, autoflush=False, bind=engine)
Base = declarative_base()
