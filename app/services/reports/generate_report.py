from datetime import date
from typing import Any

from app import config
from app.models import BetItem, WorkThread, RateItem
from app.models.statistic.total import TotalStatistic
from app.services.datetime_utils import get_moth_range, date_to_datetime
from app.services.rates import OpenExchangeRates
from app.services.rates.utils import find_rate_and_convert


async def generate_report(month: int, year: int) -> dict[int, TotalStatistic]:
    bets_log = await get_mont_bets(month, year)
    rates = await get_month_rates(month, year)
    total_statistics = {}
    async with OpenExchangeRates(config.OER_TOKEN) as oer:
        for bet_item in bets_log:
            thread: WorkThread = bet_item.worker_thread.work_thread
            day = thread.start.date()
            search_kwargs = dict(currency=bet_item.currency, day=day, oer=oer, rates=rates)
            bet = await find_rate_and_convert(value=bet_item.bet, **search_kwargs)
            result = await find_rate_and_convert(value=bet_item.result, **search_kwargs)
            total_statistic = TotalStatistic(
                day=day,
                id=thread.id,
                total_bet_eur=bet,
                total_result_eur=result + bet,
                total_payment_eur=result
            )
            append_in_statistic_in_dict(total_statistics, thread.id, total_statistic)
    return total_statistics


async def get_mont_threads(month, year) -> list[WorkThread]:
    date_start, date_stop = get_moth_range(month, year)
    return await WorkThread \
        .filter(start__gte=date_to_datetime(date_start)) \
        .filter(start__lte=date_to_datetime(date_stop)) \
        .all()


async def get_mont_bets(month, year) -> list[BetItem]:
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


def append_in_statistic_in_dict(
        collection: dict[int, TotalStatistic], key: int, value: TotalStatistic):
    try:
        collection[key].total_bet_eur += value.total_bet_eur
        collection[key].total_result_eur += value.total_result_eur
        collection[key].total_payment_eur += value.total_payment_eur
    except KeyError:
        collection[key] = value

