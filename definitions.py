import os

from api.database import SessionLocal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
