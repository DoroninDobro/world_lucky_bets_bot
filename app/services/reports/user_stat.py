from app.models import UserBetsStat, DataTimeRange
from app.models.config.currency import CurrenciesConfig
from app.models.db import WorkThread, User
from app.models.statistic.full_user_stats import FullUserStat
from app.models.statistic.transaction import TransactionStatData
from app.services.balance import get_balance_events
from app.services.rates.converter import RateConverter
from app.services.reports.common import get_mont_bets


async def generate_user_report(
        date_range: DataTimeRange,
        converter: RateConverter,
        config: CurrenciesConfig,
) -> dict[int, FullUserStat]:
    user_bets = await generate_user_bets_report(date_range=date_range, converter=converter, config=config)
    users: dict[int, list[UserBetsStat]] = {}
    for bet_stat in user_bets:
        users.setdefault(bet_stat.user.id, []).append(bet_stat)
    result = {}
    for id_, bets in users.items():
        if not bets:
            continue
        transactions = await generate_user_transactions_report(
            date_range=date_range, user=bets[0].user, converter=converter, config=config,
        )
        result[id_] = FullUserStat(bets=bets, transactions=transactions)
    return result


async def generate_user_bets_report(
        date_range: DataTimeRange,
        converter: RateConverter,
        config: CurrenciesConfig,
) -> list[UserBetsStat]:
    bets_log = await get_mont_bets(date_range)
    user_statistics = []
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


async def generate_user_transactions_report(
        date_range: DataTimeRange, user: User, converter: RateConverter, config: CurrenciesConfig,
) -> list[TransactionStatData]:
    balance_events = await get_balance_events(user=user, date_range=date_range)
    return [
        TransactionStatData(
            id=event.id,
            at=event.at,
            user=user,
            author_id=event.get_author_id(),
            currency=config.currencies[event.currency],
            amount=event.delta,
            amount_eur=await converter.find_rate_and_convert(
                value=event.delta,
                currency=event.currency,
                day=event.at,
                currency_to=config.default_currency.iso_code,
            ),
            bet_log_item_id=event.get_bet_item_id(),
            balance_event_type=event.type_,
            comment=event.comment,
        )
        for event in balance_events
    ]
