import asyncio
import typing

from aiogram import Bot, types
from loguru import logger
from tortoise.transactions import in_transaction

from app import config, keyboards as kb
from app.models import WorkThread, WorkerInThread, User, AdditionalText
from app.models.work_thread import check_thread_running
from app.services.additional_text import (
    get_enable_workers,
    create_send_workers,
    get_disable_workers,
    get_workers
)
from app.services.msg_cleaner_on_fail import msg_cleaner


thread_results = typing.List[typing.Tuple[User, int, float]]


async def start_new_thread(photo_file_id: str, admin: User, bot: Bot) -> WorkThread:
    async with in_transaction() as connection, msg_cleaner() as transaction_messages:
        created_thread = WorkThread(start_photo_file_id=photo_file_id, admin_id=admin.id)
        await created_thread.save(using_db=connection)

        msg_to_workers = await bot.send_photo(
            chat_id=config.WORKERS_CHAT_ID,
            photo=photo_file_id,
            reply_markup=kb.get_agree_work(created_thread.id)
        )
        transaction_messages.append(msg_to_workers)

        msg_to_admin = await bot.send_photo(
            chat_id=admin.id,
            photo=photo_file_id,
            caption=f"Сообщение отправлено, thread_id = {created_thread.id}",
            reply_markup=kb.get_stop_kb(created_thread.id)
        )
        transaction_messages.append(msg_to_admin)

        log_chat_message = await bot.send_photo(
            chat_id=config.ADMIN_LOG_CHAT_ID,
            photo=photo_file_id,
            caption=f"Начат новый матч от {admin.mention_link} thread_id = {created_thread.id}"
        )
        transaction_messages.append(log_chat_message)

        created_thread.log_chat_message_id = log_chat_message
        created_thread.start_message_id = msg_to_admin.message_id
        await created_thread.save(using_db=connection)
        return created_thread


async def get_thread(message_id: int) -> WorkThread:
    return await WorkThread.get(start_message_id=message_id)


@check_thread_running
async def add_info_to_thread(text: str, *, thread: WorkThread):
    async with in_transaction() as connection:
        a_t = await AdditionalText.create(text=text, thread=thread, using_db=connection)
        workers = await create_send_workers(await get_workers_from_thread(thread=thread), a_t, using_db=connection)
    return a_t, workers


async def stop_thread(thread_id: int) -> WorkThread:
    async with in_transaction() as connection:
        thread = await WorkThread.get(id=thread_id)
        thread.stopped = True
        await thread.save(using_db=connection)
        return thread


@check_thread_running
async def start_mailing(a_text: AdditionalText, bot: Bot, *, thread: WorkThread):
    async with in_transaction() as conn, msg_cleaner() as transaction_messages:
        enable_workers = await get_enable_workers(a_text)
        for enable_worker, worker_start_thread_message_id in enable_workers:
            msg = await bot.send_message(
                chat_id=enable_worker.id,
                text=a_text.text,
                reply_to_message_id=worker_start_thread_message_id,
            )
            transaction_messages.append(msg)
            await asyncio.sleep(0.1)
        enable_workers_user = [worker for worker, _ in enable_workers]
        log_msg = await send_log_mailing(a_text, bot, enable_workers_user, thread.log_chat_message_id)
        transaction_messages.append(log_msg)

        if a_text.is_disinformation:
            disinformation_log_msg_text = await render_disinformation_log(
                a_text,
                enable_workers_user,
                [worker.worker for worker in await get_workers(a_text)]
            )
            disinformation_log_msg = await bot.send_message(
                chat_id=config.USER_LOG_CHAT_ID,
                text=disinformation_log_msg_text,
            )
            transaction_messages.append(disinformation_log_msg)

        a_text.is_draft = False
        await a_text.save(using_db=conn)


async def send_log_mailing(
        a_text: AdditionalText,
        bot: Bot,
        workers: typing.List[User],
        reply_to: int
) -> types.Message:

    enable_workers_mentions = "\n".join([worker.mention_link for worker in workers])
    disable_workers_mention = "\n".join([worker.mention_link for worker in await get_disable_workers(a_text)])
    text = "Сообщение"
    text += ' ‼️является приватной инфой‼️' if a_text.is_disinformation else ''
    text += f":\n{a_text.text}\n"
    if enable_workers_mentions:
        text += f"Список пользователей, получивших сообщение сразу:\n{enable_workers_mentions}\n"
    if disable_workers_mention:
        text += f"Список пользователей, отправка которым была отменена:\n{disable_workers_mention}\n"

    return await bot.send_message(
        chat_id=config.ADMIN_LOG_CHAT_ID,
        text=text,
        reply_to_message_id=reply_to
    )


async def render_disinformation_log(
        a_text: AdditionalText,
        enable_workers: typing.List[User],
        all_workers: typing.List[User],
) -> str:
    text_parts = [
        f"Матч <b>{a_text.get_thread_id()}</b>",
        f"Сообщние: <b>{a_text.text}</b>",
    ]
    if enable_workers:
        text_parts.append("Приватно получили:")
        for enable_worker in enable_workers:
            text_parts.append(enable_worker.mention_link)
    if all_workers:
        text_parts.append("Всего участвовали на момент отправки:")
        for worker in all_workers:
            text_parts.append(worker.mention_link)
    else:
        text_parts.append("Участников на момент отправки не было")
    return "\n".join(text_parts)


@check_thread_running
async def get_workers_from_thread(*, thread: WorkThread) -> typing.List[User]:
    workers_in_thread: typing.List[WorkerInThread] = await thread.workers
    if workers_in_thread:
        return [await worker.worker for worker in workers_in_thread]
    else:
        return []


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
    await bot.send_message(
        chat_id=config.ADMIN_LOG_CHAT_ID,
        text=f"Матч thread_id={thread.id} успешно завершён",
        reply_to_message_id=thread.log_chat_message_id,
    )
