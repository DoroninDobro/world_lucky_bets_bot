from datetime import datetime

from app import config


def get_current_datetime_in_format() -> str:
    now = datetime.now(tz=config.tz_view)
    return now.strftime("%d %B\n%H:%M")
