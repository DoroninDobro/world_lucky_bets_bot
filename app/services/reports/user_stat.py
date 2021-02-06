from app import config
from app.models import UserStat, WorkThread
from app.services.rates import OpenExchangeRates
from app.services.rates.utils import find_rate_and_convert
from app.services.reports.common import get_mont_bets, get_month_rates


async def generate_user_report(month: int, year: int) -> list[UserStat]:
    bets_log = await get_mont_bets(month, year)
    rates = await get_month_rates(month, year)
    user_statistics = []
    async with OpenExchangeRates(config.OER_TOKEN) as oer:
        for bet_item in bets_log:
            thread: WorkThread = bet_item.worker_thread.work_thread
            day = thread.start.date()
            search_kwargs = dict(currency=bet_item.currency, day=day, oer=oer, rates=rates)
            bet = await find_rate_and_convert(value=bet_item.bet, **search_kwargs)
            result = await find_rate_and_convert(value=bet_item.result, **search_kwargs)
            user_stat = UserStat(
                user=bet_item.worker_thread.worker,
                day=day,
                id=thread.id,
                total_bet=f"{bet_item.bet} {bet_item.currency}",
                total_result=f"{result + bet} {bet_item.currency}",
                total_payment=f"{result} {bet_item.currency}",
                total_bet_eur=bet,
                total_result_eur=result + bet,
                total_payment_eur=result,
            )
            user_statistics.append(user_stat)
    return user_statistics

