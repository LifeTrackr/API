import os

from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
db_host = os.environ["DB_HOST"]
# Extract port from db_host if present,
# otherwise use DB_PORT environment variable.
host_args = db_host.split(":")
if len(host_args) == 1:
    db_hostname = db_host
    db_port = os.environ["DB_PORT"]
elif len(host_args) == 2:
    db_hostname, db_port = host_args[0], int(host_args[1])

engine = create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
    engine.url.URL.create(
        drivername="mysql+pymysql",
        username=db_user,  # e.g. "my-database-user"
        password=db_pass,  # e.g. "my-database-password"
        host=db_hostname,  # e.g. "127.0.0.1"
        port=db_port,  # e.g. 3306
        database=db_name,  # e.g. "my-database-name"
    )
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
