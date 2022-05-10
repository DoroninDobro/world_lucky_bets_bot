from aiogram import Bot

from app.models.config import Config
from app.models.data.bet import Bet
from app.models.db import User, WorkerInThread, BetItem
from app.services.balance import add_balance_event_and_notify
from app.services.status import create_transactions_by_bet
from app.view.datetime_utils import get_current_datetime_in_format
from app.utils.exceptions import UserPermissionError


async def save_new_betting_odd(bet: Bet, bot: Bot, config: Config):
    worker_in_thread = await WorkerInThread.get(worker=bet.user, work_thread_id=bet.thread_id)
    bet_item = await BetItem.create(
        worker_thread=worker_in_thread,
        bet=bet.bet,
        result=bet.result_without_salary,
        currency=bet.currency.iso_code,
        bookmaker_id=bet.bookmaker_id,
    )
    await bot.send_message(
        config.app.chats.user_log,
        f"{get_current_datetime_in_format(config)} - "
        f"{await bet_item.get_full_printable()} at match {bet.thread_id}",
        protect_content=False,
    )
    transactions = await create_transactions_by_bet(bet_dto=bet, bet=bet_item)
    for transaction in transactions:
        await add_balance_event_and_notify(transaction, bot, config.app.chats)
    return bet_item


async def remove_bet_item(bet_item_id: int, removing_by_user: User, config: Config):
    bet_item = await BetItem.get(id=bet_item_id)
    if removing_by_user.id in config.app.admins:
        await bet_item.delete()
        return bet_item
    await bet_item.fetch_related("worker_thread")
    # noinspection PyUnresolvedReferences
    if bet_item.worker_thread.worker_id == removing_by_user.id:
        await bet_item.delete()
        return bet_item
    raise UserPermissionError("You must be author or admin for remove that bet item")

