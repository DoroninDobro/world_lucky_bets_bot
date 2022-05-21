from app.models import TotalStatistic, DataTimeRange
from app.models.config.currency import CurrenciesConfig
from app.models.db import WorkThread
from app.services.rates.converter import RateConverter
from app.services.reports.common import get_mont_bets


async def generate_total_report(
        date_range: DataTimeRange,
        converter: RateConverter,
        config: CurrenciesConfig,
) -> dict[int, TotalStatistic]:
    bets_log = await get_mont_bets(date_range)
    total_statistics = {}
    for bet_item in bets_log:
        thread: WorkThread = bet_item.worker_thread.work_thread
        day = thread.start.date()
        search_kwargs = dict(
            currency=bet_item.currency, day=day, currency_to=config.default_currency.iso_code,
        )
        bet = await converter.find_rate_and_convert(value=bet_item.bet, **search_kwargs)
        result = await converter.find_rate_and_convert(value=bet_item.result, **search_kwargs)
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
