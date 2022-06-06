from datetime import datetime, time
from decimal import Decimal

from aiogram import Bot
from tortoise.backends.base.client import TransactionContext
from tortoise.transactions import in_transaction

from app.models import DatetimeRange, data
from app.models.config import Config
from app.models.config.app_config import ChatsConfig
from app.models.db import User, BalanceEvent, BetItem
from app.models.config.currency import CurrenciesConfig
from app.models.data.transaction import TransactionData
from app.models.enum.blance_event_type import BalanceEventType
from app.rendering.balance import render_balance
from app.services.datetime_utils import get_last_month_first_day
from app.services.rates import OpenExchangeRates
from app.services.rates.converter import RateConverter
from app.utils.exceptions import UserPermissionError


async def get_balance_sum(user: User) -> dict[str, Decimal]:
    sql = """
    select currency, sum(delta) from balance_events
    where user_id = $1 
    GROUP BY currency
    """
    async with in_transaction() as conn:
        count, balances = await conn.execute_query(sql, (user.id, ))
        result = {}
        for record in balances:
            result[record["currency"]] = record["sum"]
        return result


async def calculate_balance(user: User, oer: OpenExchangeRates, config: CurrenciesConfig) -> data.Balance:
    balances = await get_balance_sum(user)
    amounts = {}
    balance_sum = Decimal(0)
    for currency, value in balances.items():
        converter = RateConverter(oer=oer, date_range=DatetimeRange.today())
        balance_sum += await converter.find_rate_and_convert(
            value=value,
            currency=currency,
            day=None,
            currency_to=config.default_currency.iso_code,
        )
        amounts[config.currencies[currency]] = value
    return data.Balance(amount=amounts, amount_eur=balance_sum)


async def add_balance_event(transaction_data: TransactionData, conn: TransactionContext = None) -> BalanceEvent:
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
    await balance_event.save(using_db=conn)
    return balance_event


async def get_last_balance_events(user: User, limit: int = 12) -> list[BalanceEvent]:
    return await BalanceEvent\
        .filter(user=user)\
        .filter(at__gt=datetime.combine(date=get_last_month_first_day(), time=time()))\
        .order_by("-at")\
        .limit(limit)\
        .all()


async def get_balance_events(user: User, date_range: DatetimeRange) -> list[BalanceEvent]:
    return await BalanceEvent \
        .filter(user=user) \
        .filter(at__gte=date_range.start) \
        .filter(at__lte=date_range.stop) \
        .order_by("at") \
        .all()


async def add_balance_event_and_notify(
        transaction: TransactionData,
        bot: Bot,
        config: ChatsConfig,
        currencies: CurrenciesConfig,
        conn: TransactionContext = None,
):
    balance_event = await add_balance_event(transaction, conn)
    if balance_event.type_ in (BalanceEventType.USER, BalanceEventType.ADMIN):
        await bot.send_message(
            config.user_log,
            text=await balance_event.format_log(),
        )
    if balance_event.type_ == BalanceEventType.SALARY:
        await bot.send_message(
            transaction.user_id,
            balance_event.format_user(currencies)
        )


async def notify_new_balance(bot: Bot, config: CurrenciesConfig, user: User, oer: OpenExchangeRates):
    balance = await calculate_balance(user, oer, config)
    await bot.send_message(
        user.id,
        f"your new balance is {render_balance(balance, config.default_currency)}",
    )


async def remove_transaction(transaction_id: int, removed_by: User, config: Config):
    if removed_by.id not in config.app.admins:
        raise UserPermissionError("only for admins!")
    transaction = await BalanceEvent.get(id=transaction_id)
    if transaction.type_ not in (BalanceEventType.USER, BalanceEventType.ADMIN):
        raise UserPermissionError(
            text=(
                f"no one can delete automatic transaction. "
                f"Please delete bet item {transaction.get_bet_item_id()} instead"
            )
        )
    result = TransactionData.from_db(transaction, config.currencies)
    await transaction.delete()
    return result
