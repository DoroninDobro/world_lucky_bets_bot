from app.models import UserStat, DataTimeRange
from app.models.config.currency import CurrenciesConfig
from app.models.db import WorkThread
from app.services.rates import OpenExchangeRates
from app.services.rates.utils import find_rate_and_convert
from app.services.reports.common import get_mont_bets, get_month_rates


async def generate_user_report(date_range: DataTimeRange, config: CurrenciesConfig) -> list[UserStat]:
    bets_log = await get_mont_bets(date_range)
    rates = await get_month_rates(date_range)
    user_statistics = []
    async with OpenExchangeRates(config.oer_api_token) as oer:
        for bet_item in bets_log:
            thread: WorkThread = bet_item.worker_thread.work_thread
            day = thread.start.date()
            search_kwargs = dict(
                currency=bet_item.currency, day=day, oer=oer, rates=rates, currency_to=config.default_currency.iso_code,
            )
            bet = await find_rate_and_convert(value=bet_item.bet, **search_kwargs)
            result = await find_rate_and_convert(value=bet_item.result, **search_kwargs)
            user_stat = UserStat(
                user=bet_item.worker_thread.worker,
                day=day,
                thread=thread,
                total_bet=bet_item.bet,
                total_result=bet_item.result - bet_item.bet,
                total_payment=bet_item.result,
                currency=config.currencies[bet_item.currency],
                total_bet_eur=bet,
                total_result_eur=result - bet,
                total_payment_eur=result,
                bookmaker=bet_item.bookmaker,
                bet_item=bet_item,
            )
            user_statistics.append(user_stat)
    return user_statistics

