from dataclasses import dataclass
from datetime import date, timedelta, datetime, time

from app.services.datetime_utils import get_last_month_first_day


@dataclass
class DataTimeRange:
    start: datetime
    stop: datetime

    def __post_init__(self):
        if self.start > self.stop:
            raise ValueError("in data range 'start' can't be greater that 'stop'")

    @classmethod
    def get_month_range(cls, month: int, year: int):
        start = date(year, month, 1)
        if month == 12:
            stop = date(year + 1, 1, 1)
        else:
            stop = date(year, month + 1, 1)
        return cls(start=date_to_datetime(start), stop=date_to_datetime(stop))

    @classmethod
    def get_last_month_range(cls):
        last_month = get_last_month_first_day()
        return cls.get_month_range(month=last_month.month, year=last_month.year)

    @classmethod
    def get_current_month_range(cls):
        today = datetime.now()
        return cls.get_month_range(month=today.month, year=today.year)

    @classmethod
    def get_current_week_range(cls):
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
        stop = start + timedelta(days=7)
        return cls(start, stop)

    @classmethod
    def get_all_time_range(cls):
        first_time = date.min
        last_time = date.max
        return cls(start=date_to_datetime(first_time), stop=date_to_datetime(last_time))

    @classmethod
    def from_date(cls, date_: date):
        date_as_dt = datetime.combine(date=date_, time=time())
        return cls(start=date_as_dt, stop=date_as_dt)

    def __repr__(self):
        return f"{self.start.date().isoformat()} - " \
               f"{(self.stop.date() - timedelta(days=1)).isoformat()}"


def date_to_datetime(day: date) -> datetime:
    return datetime.combine(day, time(0, 0, 0, 0))
