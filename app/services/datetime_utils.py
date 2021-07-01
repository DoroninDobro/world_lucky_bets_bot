from datetime import datetime, date, time

from app import config


def get_current_datetime_in_format() -> str:
    now = datetime.now(tz=config.tz_view)
    return f"{format_date(now.date())}\n{format_time(now.time())}"


def format_date(date_: date) -> str:
    return f"{date_.day} {get_ru_month_name(date_)}"


# TODO -  Я ПРО ЭТО:
def get_ru_month_name(date_: date) -> str:
    return [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ][date_.month - 1]


def format_time(time_: time):
    return time_.strftime("%H:%M")


if __name__ == '__main__':
    print(get_current_datetime_in_format())
