from datetime import datetime
from datetime import timedelta


def check_trigger(delta: timedelta, db_time: datetime, last_trigger: datetime):
    return db_time > (last_trigger + delta)
