from dataclasses import dataclass
from datetime import date, timedelta, datetime, time


@dataclass
class DataRange:
    start: date
    stop: date

    def __post_init__(self):
        if self.start > self.stop:
            raise ValueError("in data range 'start' can't be greater that 'stop'")

    @classmethod
    def get_month_range(cls, month: int, year: int):
        start = date(year, month, 1)
        stop = date(year, month + 1, 1) - timedelta(days=1)
        return cls(start=start, stop=stop)

    @classmethod
    def get_last_month_range(cls):
        today = datetime.now()
        if today.month > 1:
            return cls.get_month_range(month=today.month - 1, year=today.year)
        return cls.get_month_range(month=12, year=today.year - 1)

    @classmethod
    def get_current_month_range(cls):
        today = datetime.now()
        return cls.get_month_range(month=today.month, year=today.year)

    @classmethod
    def get_all_time_range(cls):
        first_time = date.min
        today = datetime.now().date()
        return cls(start=first_time, stop=today)

    def __repr__(self):
        return f"{self.start.isoformat()} - {self.stop.isoformat()}"


def date_to_datetime(day: date) -> datetime:
    return datetime.combine(day, time(0, 0, 0, 0))
