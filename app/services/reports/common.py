from datetime import date

from app.models.db import BetItem, RateItem, User
from app.models import DataTimeRange


async def get_mont_bets(date_range: DataTimeRange) -> list[BetItem]:
    return await BetItem \
        .filter(worker_thread__work_thread__start__gte=date_range.start) \
        .filter(worker_thread__work_thread__start__lt=date_range.stop) \
        .prefetch_related(
            "bookmaker",
            "worker_thread",
            "worker_thread__work_thread",
            "worker_thread__worker"
        ).all()


async def get_thread_bets(thread_id: int) -> list[BetItem]:
    return await BetItem \
        .filter(worker_thread__work_thread_id=thread_id) \
        .prefetch_related(
            "bookmaker",
            "worker_thread",
            "worker_thread__worker"
        ).all()


async def get_month_rates(date_range: DataTimeRange) -> dict[date: list[RateItem]]:
    rates = await RateItem\
        .filter(at__gte=date_range.start.date())\
        .filter(at__lte=date_range.stop.date())\
        .order_by("at")
    result = {}
    for rate in rates:
        try:
            result[rate.at][rate.currency] = rate
        except KeyError:
            result[rate.at] = {rate.currency: rate}
    return result


def clear_name_for_excel(name: str):
    return "".join(filter(lambda x: x not in r'\/?*[]:!', name))


def excel_bets_caption_name(user: User) -> str:
    result = clear_name_for_excel(user.fullname) or user.username or str(user.id)
    return trim_for_excel_caption_len(result)


def trim_for_excel_caption_len(caption: str) -> str:
    return caption[:32]
