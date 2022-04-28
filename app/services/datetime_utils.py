from datetime import datetime

from app.models.config import Config


def get_current_datetime_in_format(config: Config) -> str:
    now = datetime.now(tz=config.tz_view)
    return now.strftime("%d %B\n%H:%M")
