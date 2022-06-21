from api.database import SessionLocal, SessionLocalAutocommit


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_autocommit_db():
    db_autocommit = SessionLocalAutocommit()
    try:
        yield db_autocommit
    finally:
        db_autocommit.close()
