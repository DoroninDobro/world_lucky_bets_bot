from aiogram import Bot
from tortoise.transactions import in_transaction

from app.models.config import Config
from app.models.data.bet import Bet
from app.models.db import User, WorkerInThread, BetItem
from app.services.balance import add_balance_event_and_notify, notify_new_balance
from app.services.rates import OpenExchangeRates
from app.services.status import create_transactions_by_bet
from app.utils.exceptions import UserPermissionError


async def save_new_betting_odd(bet: Bet, bot: Bot, config: Config, oer: OpenExchangeRates):
    async with in_transaction() as conn:
        worker_in_thread = await WorkerInThread.get(worker=bet.user, work_thread_id=bet.thread_id)
        bet_item = await BetItem.create(
            worker_thread=worker_in_thread,
            bet=bet.bet,
            result=bet.result_without_salary,
            currency=bet.currency.iso_code,
            bookmaker_id=bet.bookmaker_id,
            using_db=conn,
        )
        await bot.send_message(
            config.app.chats.user_log,
            f"{await bet_item.get_full_printable()} #️⃣{bet.thread_id}",
            protect_content=False,
        )
        transactions = create_transactions_by_bet(bet_dto=bet, bet=bet_item)
        for transaction in transactions:
            await add_balance_event_and_notify(transaction, bot, config.app.chats, config.currencies, conn)
    await notify_new_balance(bot, config.currencies, bet.user, oer)
    return bet_item


async def remove_bet_item(bet_item_id: int, removing_by_user: User, config: Config):
    async with in_transaction() as conn:
        bet_item = await BetItem.get(id=bet_item_id)
        if removing_by_user.id in config.app.admins:
            return await remove_bet_item_cascade(bet_item, conn)
        await bet_item.fetch_related("worker_thread", using_db=conn)
        # noinspection PyUnresolvedReferences
        if bet_item.worker_thread.worker_id == removing_by_user.id:
            return await remove_bet_item_cascade(bet_item, conn)
    raise UserPermissionError("You must be author or admin for remove that bet item")


async def remove_bet_item_cascade(bet_item: BetItem, conn) -> BetItem:
    await bet_item.fetch_related("balance_events", using_db=conn)
    for event in bet_item.balance_events:
        await event.delete(using_db=conn)
    await bet_item.delete(using_db=conn)
    return bet_item

