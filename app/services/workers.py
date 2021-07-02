from datetime import datetime

from aiogram import Bot

from app import config
from app.models import User, WorkThread, WorkerInThread
from app.models.db.work_thread import check_thread_running

OLD_MESSAGE_SEPARATOR = "\n.\n"


@check_thread_running
async def add_worker_to_thread(user: User, message_id: int, bot: Bot, *, thread: WorkThread) -> WorkerInThread:
    worker_in_thread = await WorkerInThread.create(
        work_thread=thread, worker=user, message_id=message_id,
    )
    await bot.send_message(
        config.USER_LOG_CHAT_ID,
        f"{datetime.now(tz=config.tz_view)} - {user.mention_link} "
        f"joined to work on the match {thread.id}",
    )
    texts = await thread.additional_texts.filter(is_draft=False, is_disinformation=False).all()
    if texts:
        send_text = OLD_MESSAGE_SEPARATOR.join([text.text for text in texts])
        await bot.send_message(chat_id=user.id, text=send_text,
                               reply_to_message_id=message_id)
    return worker_in_thread


async def get_worker_in_thread(message_id: int, user: User):
    return await WorkerInThread.get(worker=user, message_id=message_id)
