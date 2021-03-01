from app import config
from app.models import TotalStatistic, WorkThread, DataTimeRange
from app.services.rates import OpenExchangeRates
from app.services.rates.utils import find_rate_and_convert
from app.services.reports.common import get_mont_bets, get_month_rates


async def generate_total_report(date_range: DataTimeRange) -> dict[int, TotalStatistic]:
    bets_log = await get_mont_bets(date_range)
    rates = await get_month_rates(date_range)
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
                thread=thread,
                total_bet_eur=bet,
                total_result_eur=result - bet,
                total_payment_eur=result,
            )
            append_in_statistic_in_dict(total_statistics, thread.id, total_statistic)
    return total_statistics


def append_in_statistic_in_dict(
        collection: dict[int, TotalStatistic], key: int, value: TotalStatistic):
    try:
        collection[key].total_bet_eur += value.total_bet_eur
        collection[key].total_result_eur += value.total_result_eur
        collection[key].total_payment_eur += value.total_payment_eur
    except KeyError:
        collection[key] = value
