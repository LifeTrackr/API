import sqlalchemy.exc
from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.responses import JSONResponse

from .utils.load_env import Env

env = Env()
host_args = env.db_host.split(":")
if len(host_args) == 1:
    db_hostname, db_port = env.db_host, env.db_port
elif len(host_args) == 2:
    db_hostname, db_port = host_args[0], int(host_args[1])
else:
    raise KeyError("Error: Host args > 2")

engine = create_engine(engine.url.URL.create(drivername="postgresql+psycopg2", username=env.db_user, port=db_port,
                                             password=env.db_pass, host=env.db_host, database=env.db_name))
print(f"[info] host {env.db_host}")


def db_add(db: Session, item):
    db.add(item)
    try:
        db.commit()
    except Exception as e:
        msg = {"error": "Database validation error"}
        if not env.production:
            msg["db_msg"] = e.args[0]
            return JSONResponse(
                status_code=422,
                content=msg,
            )
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
        if not env.production:
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
