from datetime import date

from app.models import BetItem, RateItem
from app.services.datetime_utils import get_moth_range, date_to_datetime


async def get_mont_bets(month: int, year: int) -> list[BetItem]:
    date_start, date_stop = get_moth_range(month, year)
    return await BetItem \
        .filter(worker_thread__work_thread__start__gte=date_to_datetime(date_start)) \
        .filter(worker_thread__work_thread__start__lte=date_to_datetime(date_stop)) \
        .prefetch_related(
            "worker_thread",
            "worker_thread__work_thread",
            "worker_thread__worker"
        ).all()


async def get_month_rates(month: int, year: int) -> dict[date: list[RateItem]]:
    date_start, date_stop = get_moth_range(month, year)
    rates = await RateItem.filter(at__gte=date_start).filter(at__lte=date_stop).order_by("at")
    result = {}
    for rate in rates:
        try:
            result[rate.at][rate.currency] = rate
        except KeyError:
            result[rate.at] = {rate.currency: rate}
    return result