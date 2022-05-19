from app.models import UserBetsStat, DataTimeRange
from app.models.config.currency import CurrenciesConfig
from app.models.db import WorkThread
from app.models.statistic.full_user_stats import FullUserStat
from app.services.rates import OpenExchangeRates
from app.services.rates.converter import RateConverter
from app.services.reports.common import get_mont_bets, get_month_rates


async def generate_user_report(date_range: DataTimeRange, config: CurrenciesConfig) -> dict[int, FullUserStat]:
    user_bets = await generate_user_bets_report(date_range=date_range, config=config)
    users = {}
    for bet_stat in user_bets:
        users.setdefault(bet_stat.user.id, []).append(bet_stat)
    return {id_: FullUserStat(bets=bets, transactions=None) for id_, bets in users.items()}


async def generate_user_bets_report(date_range: DataTimeRange, config: CurrenciesConfig) -> list[UserBetsStat]:
    bets_log = await get_mont_bets(date_range)
    rates = await get_month_rates(date_range)
    user_statistics = []
    async with OpenExchangeRates(config.oer_api_token) as oer:
        converter = RateConverter(oer=oer, rates=rates)
        for bet_item in bets_log:
            thread: WorkThread = bet_item.worker_thread.work_thread
            day = thread.start.date()
            search_kwargs = dict(
                currency=bet_item.currency, day=day, currency_to=config.default_currency.iso_code,
            )
            bet = await converter.find_rate_and_convert(value=bet_item.bet, **search_kwargs)
            result = await converter.find_rate_and_convert(value=bet_item.result, **search_kwargs)
            user_stat = UserBetsStat(
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

