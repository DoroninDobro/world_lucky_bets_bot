import asyncio
import typing
from datetime import datetime

from aiogram import Bot, types
from loguru import logger
from tortoise.transactions import in_transaction

from app.view.keyboards import admin as kb_admin
from app.view.keyboards import worker as kb_worker
from app.models.db import WorkThread, WorkerInThread, User, AdditionalText
from app.models.config import Config
from app.models.db.work_thread import check_thread_running
from app.services.additional_text import (
    get_enable_workers,
    create_send_workers,
    get_disable_workers,
    get_workers
)
from app.services.msg_cleaner_on_fail import msg_cleaner
from app.utils.text_utils import remove_usernames

thread_results = typing.List[typing.Tuple[User, int, float]]


async def start_new_thread(
        photo_file_id: str, admin: User, bot: Bot, config: Config,
) -> WorkThread:
    async with in_transaction() as connection, \
               msg_cleaner() as transaction_messages:
        created_thread = WorkThread(start_photo_file_id=photo_file_id,
                                    admin_id=admin.id)
        await created_thread.save(using_db=connection)

        msg_to_workers = await bot.send_photo(
            chat_id=config.app.chats.workers,
            photo=photo_file_id,
            caption=f"{created_thread.id}",
            reply_markup=kb_worker.get_agree_work(created_thread.id)
        )
        transaction_messages.append(msg_to_workers)

        msg_to_admin = await bot.send_photo(
            chat_id=admin.id,
            photo=photo_file_id,
            caption=f"{created_thread.id}. Message sent",
            reply_markup=kb_admin.get_work_thread_admin_kb(created_thread.id),
            protect_content=False,
        )
        transaction_messages.append(msg_to_admin)

        log_chat_message = await bot.send_photo(
            chat_id=config.app.chats.admin_log,
            photo=photo_file_id,
            caption=f"{created_thread.id}. "
                    f"Started a new match from {admin.id}",
        )
        transaction_messages.append(log_chat_message)

        for_admins_no_usernames_message = await bot.send_photo(
            chat_id=config.app.chats.admins_without_usernames_log,
            photo=photo_file_id,
            caption=str(created_thread.id),
        )
        transaction_messages.append(for_admins_no_usernames_message)

        created_thread.log_chat_message_id = log_chat_message.message_id
        created_thread.log_chat_for_admins_without_usernames_message_id = for_admins_no_usernames_message.message_id
        created_thread.start_message_id = msg_to_admin.message_id
        created_thread.workers_chat_message_id = msg_to_workers.message_id
        await created_thread.save(using_db=connection)

    return created_thread


async def get_thread(message_id: int) -> WorkThread:
    return await WorkThread.get(start_message_id=message_id)


@check_thread_running
async def add_info_to_thread(text: str, *, thread: WorkThread):
    async with in_transaction() as connection:
        a_t = await AdditionalText.create(
            text=text, thread=thread, using_db=connection,
        )
        workers = await create_send_workers(
            await get_workers_from_thread(thread=thread),
            a_t, using_db=connection,
        )
    return a_t, workers


async def stop_thread(thread_id: int) -> WorkThread:
    async with in_transaction() as connection:
        thread = await WorkThread.get(id=thread_id)
        thread.stopped = True
        await thread.save(using_db=connection)
        return thread


@check_thread_running
async def start_mailing(
        a_text: AdditionalText, bot: Bot, *, thread: WorkThread, config: Config,
):
    async with in_transaction() as conn, msg_cleaner() as transaction_messages:
        enable_workers = await get_enable_workers(a_text)
        for enable_worker, worker_start_thread_message_id in enable_workers:
            logger.info("sending additional info {a_t} to user {user}",
                        a_t=a_text, user=enable_worker.id)
            msg = await bot.send_message(
                chat_id=enable_worker.id,
                text=a_text.text,
                reply_to_message_id=worker_start_thread_message_id,
            )
            transaction_messages.append(msg)
            await asyncio.sleep(0.1)
        enable_workers_user = [worker for worker, _ in enable_workers]
        log_msg = await send_log_mailing(
            a_text, bot, enable_workers_user, thread, config,
        )
        transaction_messages.append(log_msg)

        if a_text.is_disinformation:
            disinformation_log_msg_text = await render_disinformation_log(
                a_text,
                enable_workers_user,
                [worker.worker for worker in await get_workers(a_text)]
            )
            disinformation_log_msg = await bot.send_message(
                chat_id=config.app.chats.user_log,
                text=disinformation_log_msg_text,
            )
            transaction_messages.append(disinformation_log_msg)

        a_text.is_draft = False
        a_text.sent = datetime.now(tz=config.tz_db)
        await a_text.save(using_db=conn)


async def send_log_mailing(
        a_text: AdditionalText,
        bot: Bot,
        workers: typing.List[User],
        thread: WorkThread,
        config: Config,
) -> types.Message:

    text = render_log_message_caption(a_text)

    # В этот чат отправляем только заголовок
    # (информацию о приватности инфы и текст сообщения)
    await bot.send_message(
        chat_id=config.app.chats.admins_without_usernames_log,
        text=remove_usernames(text),
        reply_to_message_id=thread.log_chat_for_admins_without_usernames_message_id
    )

    # Добавляем к заголовку список воркеров
    # и теперь можно отправлять и в обычный логчат
    text += await render_workers_lists_with_caption(a_text, workers)
    return await bot.send_message(
        chat_id=config.app.chats.admin_log,
        text=text,
        reply_to_message_id=thread.log_chat_message_id
    )


def render_log_message_caption(a_text: AdditionalText) -> str:
    text = "Message"
    text += ' ‼️is private info‼️' if a_text.is_disinformation else ''
    text += f":\n{a_text.text}\n"
    return text


async def render_workers_lists_with_caption(a_text: AdditionalText, workers: typing.List[User]) -> str:
    enable_workers_mentions = "\n".join([str(worker.id) for worker in workers])
    disable_workers_mention = "\n".join([str(worker.id) for worker in await get_disable_workers(a_text)])
    text = ""
    if enable_workers_mentions:
        text += f"List of users who received the message immediately:\n{enable_workers_mentions}\n"
    if disable_workers_mention:
        text += f"List of users whose sending was canceled:\n{disable_workers_mention}\n"
    return text


async def render_disinformation_log(
        a_text: AdditionalText,
        enable_workers: typing.List[User],
        all_workers: typing.List[User],
) -> str:
    text_parts = [
        f"Match <b>{a_text.get_thread_id()}</b>",
        f"Message: <b>{a_text.text}</b>",
    ]
    if enable_workers:
        text_parts.append("Received privately:")
        for enable_worker in enable_workers:
            text_parts.append(enable_worker.mention_link)
    if all_workers:
        text_parts.append("Total participated at the time of sending:")
        for worker in all_workers:
            text_parts.append(worker.mention_link)
    else:
        text_parts.append("There were no participants at the time of sending")
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
    await callback_query.answer(f"Match thread_id={thread_id} not found",
                                show_alert=True)
    await callback_query.message.edit_caption(
        f"Match thread_id={thread_id} not found, "
        f"maybe it was already finished",
        reply_markup=kb_admin.get_stopped_work_thread_admin_kb(thread_id),
    )


async def rename_thread(thread_id: int, new_name: str):
    thread = await WorkThread.get(id=thread_id)
    thread.name = new_name
    await thread.save()


async def send_notification_stop(thread: WorkThread, bot: Bot, config: Config):
    for worker in await thread.workers:
        user = await worker.worker
        await bot.send_message(user.id, f"Match {thread.id} is over",
                               reply_to_message_id=worker.message_id)
        await asyncio.sleep(0.5)
    notify_text = (
        f"Match {thread.name if thread.name is not None else ''} "
        f"has been successfully completed"
    )
    await bot.send_message(
        chat_id=config.app.chats.admin_log,
        text=notify_text,
        reply_to_message_id=thread.log_chat_message_id,
    )
    await bot.send_message(
        chat_id=config.app.chats.user_log,
        text=f"{thread.id}. {notify_text}",

    )
    await bot.send_message(
        chat_id=config.app.chats.admins_without_usernames_log,
        text=notify_text,
        reply_to_message_id=thread.log_chat_for_admins_without_usernames_message_id,
    )
