import asyncio
import typing

from aiogram import Bot, types
from loguru import logger
from tortoise.transactions import in_transaction

from app.models import WorkThread, WorkerInThread, User
from app.utils.exceptions import ThreadStopped


thread_results = typing.List[typing.Tuple[User, int, float]]


async def start_new_thread(photo_file_id: str, admin_id: int) -> WorkThread:
    wt = WorkThread(start_photo_file_id=photo_file_id, admin_id=admin_id)
    await wt.save()
    return wt


async def update_message_id(thread: WorkThread, message_id: int):
    thread.start_message_id = message_id
    await thread.save()


async def get_thread(message_id: int) -> WorkThread:
    return await WorkThread.get(start_message_id=message_id)


async def stop_thread(thread_id: int) -> WorkThread:
    async with in_transaction() as connection:
        thread = await WorkThread.get(id=thread_id)
        thread.stopped = True
        await thread.save(using_db=connection)
        return thread


async def start_mailing(thread: WorkThread, workers: typing.List[typing.Tuple[User, int]], text: str, bot: Bot):
    if thread.stopped:
        # noinspection PyUnresolvedReferences
        raise ThreadStopped(user_id=thread.admin_id)
    for worker, message_id in workers:
        await bot.send_message(
            chat_id=worker.id,
            text=text,
            reply_to_message_id=message_id,
        )
        await asyncio.sleep(0.1)


async def get_workers_from_thread(thread: WorkThread) -> typing.List[User]:
    workers_in_thread: typing.List[WorkerInThread] = await thread.workers
    return [
        await worker.worker for worker in workers_in_thread
    ]


async def thread_not_found(callback_query: types.CallbackQuery, thread_id: int):
    logger.error("thread {thread_id} not found", thread_id=thread_id)
    await callback_query.answer(f"Матч thread_id={thread_id} не найдён", show_alert=True)
    await callback_query.message.edit_caption(
        f"Матч thread_id={thread_id} не найден, возможно он уже был завершён",
        reply_markup=None
    )


async def get_stats(thread: WorkThread) -> thread_results:
    results: thread_results = []
    for worker in await thread.workers:
        user = await worker.worker
        money_sum = 0
        win_sum = 0
        for bet in await worker.bets:
            money_sum += bet.money
            win_sum += bet.money * bet.odd
        try:
            average_odd = win_sum / money_sum
        except ZeroDivisionError:
            average_odd = 0.0
        results.append((user, money_sum, average_odd))
    return results


def format_results_thread(results: thread_results, thread_id: int) -> str:
    text = f"Результаты матча {thread_id}:"
    total_sum = 0
    total_win_sum = 0
    for user, money_sum, average_odd in results:
        text += f"\n{user.mention_link} общая сумма {money_sum}, средний кэф {average_odd:.2f}"
        total_sum += money_sum
        total_win_sum += money_sum * average_odd
    text += f"\n\nИтого за матч: общая сумма {total_sum}"
    try:
        total_odd = total_win_sum / total_sum
    except ZeroDivisionError:
        text += "."
    else:
        text += f", средний кэф {total_odd:.2f}."
    return text


async def send_notification_stop(thread: WorkThread, bot: Bot):
    for worker in await thread.workers:
        user = await worker.worker
        await bot.send_message(user.id, f"Матч {thread.id} закончен", reply_to_message_id=worker.message_id)
        await asyncio.sleep(0.5)
