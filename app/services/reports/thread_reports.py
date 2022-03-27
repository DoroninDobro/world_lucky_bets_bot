import operator
from functools import reduce

from app import config
from app.models import WorkThread, UserStat
from app.services.rates import OpenExchangeRates
from app.services.rates.utils import find_rate_and_convert
from app.services.reports.common import get_thread_bets, get_rates_by_date


async def get_thread_report(thread_id: int) -> str:
    thread = await WorkThread.get(id=thread_id)
    report_result = f"Отчёт о матче <b>{thread.name}</b> ({thread_id}):\n"
    user_statistics = await get_user_stats(thread)
    total_bets = reduce(operator.add, map(lambda x: x.total_bet_eur, user_statistics), 0)
    report_result += f"Итого {total_bets:.2f}€ / "
    total_result = reduce(operator.add, map(lambda x: x.total_result_eur, user_statistics), 0)
    report_result += f"{total_result:.2f}€\n"
    statistics_by_user: dict[int, list[UserStat]] = {}
    for us in user_statistics:
        user_stats = statistics_by_user.setdefault(us.user.id, [])
        user_stats.append(us)
    for user_stats in statistics_by_user.values():
        user_stat: UserStat = user_stats[0]
        report_result += f"<u>#️⃣{user_stat.user.id}:</u>\n"
        sum_bet = {}
        sum_result = {}
        for user_stat in user_stats:
            sum_bet.setdefault(user_stat.bookmaker.name, 0)
            sum_bet[user_stat.bookmaker.name] += user_stat.total_bet_eur
            sum_result.setdefault(user_stat.bookmaker.name, 0)
            sum_result[user_stat.bookmaker.name] += user_stat.total_result_eur
        for bookmaker_name in sum_bet:
            report_result += f"\t{bookmaker_name} {sum_bet[bookmaker_name]:.2f}€ / {sum_result[bookmaker_name]:.2f}€\n"
    return report_result


async def get_user_stats(thread: WorkThread):
    day = thread.start.date()
    bets_log = await get_thread_bets(thread.id)
    rates = await get_rates_by_date(day)
    user_statistics = []
    async with OpenExchangeRates(config.OER_TOKEN) as oer:
        for bet_item in bets_log:
            search_kwargs = dict(currency=bet_item.currency, day=day, oer=oer, rates=rates)
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
