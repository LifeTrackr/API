from datetime import datetime
from datetime import timedelta


def check_trigger(delta: timedelta, db_time: datetime, last_trigger: datetime):
    future = last_trigger + delta
    return db_time > future
