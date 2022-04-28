from decimal import Decimal

from aiogram import Bot

from app.models.config import Config
from app.models.config.currency import Currency
from app.models import User, WorkerInThread, BetItem
from app.services.datetime_utils import get_current_datetime_in_format
from app.utils.exceptions import UserPermissionError


async def save_new_betting_odd(
        thread_id: int,
        currency: Currency,
        bet: Decimal,
        result: Decimal,
        bookmaker_id: str,
        user: User,
        bot: Bot,
        config: Config
):
    worker_in_thread = await WorkerInThread.get(worker=user, work_thread_id=thread_id)
    bet_item = await BetItem.create(
        worker_thread=worker_in_thread,
        bet=bet,
        result=result,
        currency=currency.iso_code,
        bookmaker_id=bookmaker_id,
    )
    await bot.send_message(
        config.app.chats.user_log,
        f"{get_current_datetime_in_format(config)} - "
        f"{await bet_item.get_full_printable()} at match {thread_id}",
        protect_content=False,
    )
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

