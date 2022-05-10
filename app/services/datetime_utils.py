from datetime import datetime, date


def get_last_month_first_day():
    today = datetime.now()
    if today.month > 1:
        return date(day=1, month=today.month - 1, year=today.year)
    return date(day=1, month=12, year=today.year - 1)
