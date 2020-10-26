import asyncio
import typing

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from loguru import logger
from tortoise.exceptions import DoesNotExist

from app.misc import dp

from . import keyboards as kb
from app.services.work_threads import (
    start_new_thread,
    stop_thread,
    get_thread,
    start_mailing,
    update_message_id, thread_not_found, get_stats, format_results_thread, send_notification_stop,
    get_workers_from_thread,
)
from app import config
from app.models import User, AdditionalText, SendWorkers
from ..services.additional_text import new_additional_text, create_send_workers, get_workers, get_enable_workers, \
    change_disinformation, change_worker, mark_additional_text_as_send
from ..services.remove_message import delete_message


@dp.message_handler(is_admin=True, chat_type=types.ChatType.PRIVATE, is_reply=False,
                    content_types=types.ContentType.PHOTO)
@dp.throttled(rate=0.5)
async def new_send(message: types.Message, user: User):
    logger.info("admin {user} start new thread ", user=message.from_user.id)
    photo_file_id = message.photo[-1].file_id
    thread = await start_new_thread(photo_file_id, user.id)
    await message.send_copy(config.WORKERS_CHAT_ID, reply_markup=kb.get_agree_work(thread.id))
    msg = await message.reply_photo(
        photo=photo_file_id,
        caption=f"Сообщение отправлено, thread_id = {thread.id}",
        reply_markup=kb.get_stop_kb(thread.id)
    )
    await update_message_id(thread, msg.message_id)
    await delete_message(message)


@dp.message_handler(is_admin=True, chat_type=types.ChatType.PRIVATE, is_reply=True)
async def add_new_info(message: types.Message, user: User, reply: types.Message):
    try:
        thread = await get_thread(reply.message_id)
    except DoesNotExist:
        logger.info("admin {user} send message as reply but without thread", user=user.id)
        return await message.reply("Непонятно, это сообщение не направлено на стартовое")

    logger.info("admin {user} add new info to thread {thread} ", user=user.id, thread=thread.id)
    a_t = await new_additional_text(message.html_text, thread)
    workers = await create_send_workers(await get_workers_from_thread(thread), a_t)
    await message.reply(f"Отправить информацию:\n{a_t.text}", reply_markup=kb.get_kb_menu_send(workers, a_t))


async def get_additional_text(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    additional_text_id = int(callback_data['additional_text'])
    try:
        a_t = await AdditionalText.get(id=additional_text_id)
        thread = await a_t.thread
        if thread.stopped:
            raise DoesNotExist
    except DoesNotExist:
        logger.info("admin {user} try send message without thread", user=user.id)
        await callback_query.answer("Это какая-то странная кнопка, я удалю от греха подальше", show_alert=True)
        await callback_query.message.edit_text("Тут было какое-то старое сообщение с невалидными кнопками")
        raise CancelHandler
    else:
        return a_t, thread


@dp.callback_query_handler(kb.cb_send_now.filter())
async def send_new_info_now(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)
    workers = await get_enable_workers(a_t)
    await mark_additional_text_as_send(a_t)
    asyncio.create_task(start_mailing(thread, workers, a_t.text, callback_query.bot))
    await callback_query.message.edit_text(f"Отправлено:\n{a_t.text}")


@dp.callback_query_handler(kb.cb_is_disinformation.filter())
async def change_disinformation(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)

    is_disinformation = bool(int(callback_data['is_disinformation']))
    logger.info("admin {user} mark text as {disinformation}disinformation in thread {thread}",
                user=user.id, thread=thread.id, disinformation="" if is_disinformation else "not ", )
    await change_disinformation(a_t, is_disinformation)
    await callback_query.message.edit_reply_markup(kb.get_kb_menu_send(await get_workers(a_t), a_t))


@dp.callback_query_handler(kb.cb_workers.filter())
async def change_addressee_workers(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)
    worker = await SendWorkers.get(id=int(callback_data["send_worker_id"]))
    enable = bool(int(callback_data["enable"]))

    # noinspection PyUnresolvedReferences
    user_id = worker.worker_id

    logger.info("admin {user} {change} for worker {worker} in {thread}",
                user=user.id, thread=thread.id, change="enable" if enable else "disable", worker=user_id)
    await change_worker(worker, enable)
    await callback_query.message.edit_reply_markup(kb.get_kb_menu_send(await get_workers(a_t), a_t))


@dp.callback_query_handler(kb.cb_stop.filter(), is_admin=True)
async def stop_work_thread(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    thread_id = int(callback_data['thread_id'])
    try:
        thread = await stop_thread(thread_id)
    except DoesNotExist:
        await thread_not_found(callback_query, thread_id)
    else:
        logger.info(
            "thread {thread_id} closed successfully by admin {admin}",
            thread_id=thread_id,
            admin=callback_query.from_user.id
        )
        await callback_query.answer()
        await callback_query.message.edit_caption(
            f"Матч thread_id={thread_id} успешно завершён",
            reply_markup=None
        )
        results = await get_stats(thread)
        await callback_query.bot.send_message(
            chat_id=config.USER_LOG_CHAT_ID,
            text=format_results_thread(results, thread_id)
        )
        await send_notification_stop(thread, callback_query.bot)
