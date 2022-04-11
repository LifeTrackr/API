import os

from api.database import SessionLocal
from api.database import SessionLocalAutocommit

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root


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
