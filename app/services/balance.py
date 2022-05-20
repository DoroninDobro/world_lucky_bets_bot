from datetime import datetime, time
from decimal import Decimal

from aiogram import Bot

from app.models import DataTimeRange
from app.models.config.app_config import ChatsConfig
from app.models.db import User, BalanceEvent, BetItem
from app.models.config.currency import CurrenciesConfig
from app.models.data.transaction import TransactionData
from app.models.enum.blance_event_type import BalanceEventType
from app.services.datetime_utils import get_last_month_first_day
from app.services.rates import OpenExchangeRates
from app.services.rates.converter import RateConverter
from app.services.reports.common import get_rates_by_date


async def calculate_balance(user: User, oer: OpenExchangeRates, config: CurrenciesConfig) -> Decimal:
    balance_sum = Decimal(0)
    for balance_event in await user.balance_events.all():
        balance_event: BalanceEvent
        converter = RateConverter(oer=oer, rates=await get_rates_by_date(balance_event.at))
        balance_sum += await converter.find_rate_and_convert(
            value=balance_event.delta,
            currency=balance_event.currency,
            day=balance_event.at,
            currency_to=config.default_currency.iso_code,
        )
    return balance_sum


async def add_balance_event(transaction_data: TransactionData) -> BalanceEvent:
    if bet_log_id := transaction_data.bet_log_item_id:
        bet_item = await BetItem.get(id=bet_log_id)
    else:
        bet_item = None
    balance_event = BalanceEvent(
        user_id=transaction_data.user_id,
        author_id=transaction_data.author_id,
        delta=transaction_data.amount,
        currency=transaction_data.currency.iso_code,
        comment=transaction_data.comment,
        type_=transaction_data.balance_event_type,
        bet_item=bet_item,
    )
    await balance_event.save()
    return balance_event


async def get_last_balance_events(user: User, limit: int = 12) -> list[BalanceEvent]:
    return await BalanceEvent\
        .filter(user=user)\
        .filter(at__gt=datetime.combine(date=get_last_month_first_day(), time=time()))\
        .order_by("-at")\
        .limit(limit)\
        .all()


async def get_balance_events(user: User, date_range: DataTimeRange) -> list[BalanceEvent]:
    return await BalanceEvent \
        .filter(user=user) \
        .filter(at__gte=date_range.start) \
        .filter(at__lte=date_range.stop) \
        .order_by("-at") \
        .all()


async def add_balance_event_and_notify(transaction: TransactionData, bot: Bot, config: ChatsConfig):
    balance_event = await add_balance_event(transaction)
    if balance_event.type_ in (BalanceEventType.USER, BalanceEventType.ADMIN):
        await bot.send_message(
            config.user_log,
            text=await balance_event.format_log(),
        )
