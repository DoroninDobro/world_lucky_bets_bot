from datetime import date, timedelta, datetime, time


def get_moth_range(month: int, year: int) -> tuple[date, date]:
    start = date(year, month, 1)
    stop = date(year, month + 1, 1) - timedelta(days=1)
    return start, stop


def date_to_datetime(day: date) -> datetime:
    return datetime.combine(day, time(0, 0, 0, 0))