from datetime import datetime
from decimal import Decimal

from aiogram import Bot

from app import config
from app.config.currency import Currency
from app.models import User, WorkThread, WorkerInThread, BetItem
from app.models.db.work_thread import check_thread_running
from app.services.datetime_utils import get_current_datetime_in_format

OLD_MESSAGE_SEPARATOR = "\n.\n"


@check_thread_running
async def add_worker_to_thread(user: User, message_id: int, bot: Bot, *, thread: WorkThread) -> WorkerInThread:
    worker_in_thread = await WorkerInThread.create(work_thread=thread, worker=user, message_id=message_id)
    await bot.send_message(
        config.USER_LOG_CHAT_ID,
        f"{datetime.now(tz=config.tz_view)} - {user.mention_link} присоединился к работе над матчем {thread.id}"
    )
    texts = await thread.additional_texts.filter(is_draft=False, is_disinformation=False).all()
    if texts:
        send_text = OLD_MESSAGE_SEPARATOR.join([text.text for text in texts])
        await bot.send_message(chat_id=user.id, text=send_text, reply_to_message_id=message_id)
    return worker_in_thread


async def get_worker_in_thread(message_id: int, user: User):
    return await WorkerInThread.get(worker=user, message_id=message_id)


async def save_new_betting_odd(
        thread_id: int,
        currency: Currency,
        bet: Decimal,
        result: Decimal,
        bookmaker_id: str,
        user: User,
        bot: Bot):
    worker_in_thread = await WorkerInThread.get(worker=user, work_thread_id=thread_id)
    bet_item = await BetItem.create(
        worker_thread=worker_in_thread,
        bet=bet,
        result=result,
        currency=currency.iso_code,
        bookmaker_id=bookmaker_id,
    )
    await bot.send_message(
        config.USER_LOG_CHAT_ID,
        f"{get_current_datetime_in_format()} - {user.mention_link} сделал ставку {bet_item} в матче {thread_id}"
    )
    return bet_item
