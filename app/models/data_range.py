from dataclasses import dataclass
from datetime import date, timedelta, datetime, time


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
        last_time = date.max
        return cls(start=date_to_datetime(first_time), stop=date_to_datetime(last_time))

    def __repr__(self):
        return f"{self.start.date().isoformat()} - " \
               f"{(self.stop.date() - timedelta(days=1)).isoformat()}"


def date_to_datetime(day: date) -> datetime:
    return datetime.combine(day, time(0, 0, 0, 0))
