from datetime import datetime

from aiogram import Bot

from app import config
from app.models import User, WorkThread, WorkerInThread, BetItem
from app.models.bets_log import BettingOdd
from app.utils.exceptions import ThreadStopped


async def add_worker_to_thread(user: User, thread: WorkThread, message_id: int, bot: Bot):
    if thread.stopped:
        raise ThreadStopped(user_id=user.id)
    await WorkerInThread.create(work_thread=thread, worker=user, message_id=message_id)
    await bot.send_message(
        config.USER_LOG_CHAT_ID,
        f"{datetime.now(tz=config.tz_view)} - {user.mention_link} присоединился к работе над матчем {thread.id}"
    )
    texts = await thread.additional_texts.filter(is_draft=False, is_disinformation=False).all()
    if texts:
        send_text = "\n".join([text.text for text in texts])
        await bot.send_message(chat_id=user.id, text=send_text, reply_to_message_id=message_id)


async def get_worker_in_thread(message_id: int, user: User):
    return await WorkerInThread.get(worker=user, message_id=message_id)


def get_bet_and_odd(text: str) -> BettingOdd:
    money, odd = text.split()
    return BettingOdd(int(money), float(odd))


async def save_new_betting_odd(betting_odd: BettingOdd, worker_in_thread: WorkerInThread, bot: Bot):
    user = await worker_in_thread.worker
    thread = await worker_in_thread.work_thread
    if thread.stopped:
        raise ThreadStopped(user_id=user.id)
    bet_item = await BetItem.create(worker_thread=worker_in_thread, money=betting_odd.money, odd=betting_odd.odd)
    await bot.send_message(
        config.USER_LOG_CHAT_ID,
        f"{datetime.now(tz=config.tz_view)} - {user.mention_link} сделал ставку {betting_odd} в матче {thread.id}"
    )
    return bet_item
