from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class DataRange:
    start: date
    stop: date

    @classmethod
    def get_month_range(cls, month: int, year: int):
        cls(*get_moth_range(month, year))


def get_moth_range(month: int, year: int) -> tuple[date, date]:
    start = date(year, month, 1)
    stop = date(year, month + 1, 1) - timedelta(days=1)
    return start, stop
