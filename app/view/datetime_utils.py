from datetime import datetime

from app.models.config import Config


def get_current_datetime_in_format(config: Config) -> str:
    return format_datetime(datetime.now(tz=config.tz_view))


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d %B\n%H:%M")
