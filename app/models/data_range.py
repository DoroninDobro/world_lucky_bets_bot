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


def date_to_datetime(day: date) -> datetime:
    return datetime.combine(day, time(0, 0, 0, 0))
