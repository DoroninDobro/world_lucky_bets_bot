import asyncio
import typing

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.utils.exceptions import MessageNotModified, BadRequest
from loguru import logger
from tortoise.exceptions import DoesNotExist

from app.misc import dp

from app.services.work_threads import (
    start_new_thread,
    stop_thread,
    get_thread,
    start_mailing,
    thread_not_found,
    send_notification_stop,
    add_info_to_thread,
    rename_thread,
    save_daily_rates,
)
from app import config, keyboards as kb
from app.models import User, AdditionalText, WorkThread
from ..services.additional_text import (
    get_workers,
    change_disinformation,
    change_worker,
)
from ..services.remove_message import delete_message
from ..utils.exceptions import ThreadStopped


class RenameThread(StatesGroup):
    name = State()


@dp.message_handler(commands=["start"], commands_prefix='!/', is_admin=True)
@dp.throttled(rate=3)
async def cmd_start(message: types.Message):
    """For start handler for not admin see base.py """
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.reply(
        "Hi, admin!",
        reply_markup=kb.get_reply_kb_report(),
        protect_content=False,
    )


@dp.message_handler(is_admin=True, chat_type=types.ChatType.PRIVATE, is_reply=False,
                    content_types=types.ContentType.PHOTO)
@dp.throttled(rate=0.5)
async def new_send(message: types.Message, user: User):
    photo_file_id = message.photo[-1].file_id
    try:
        thread = await start_new_thread(photo_file_id, user, message.bot)
    except Exception:
        await message.reply(
            "Something went wrong, we wrote down the problem",
            protect_content=False
        )
        logger.error(
            "admin {user} try start new thread, but failed",
            user=user.id
        )
        raise
    logger.info("admin {user} start new thread {thread}",
                user=message.from_user.id, thread=thread.id)
    await delete_message(message)
    await save_daily_rates()


@dp.message_handler(is_admin=True, chat_type=types.ChatType.PRIVATE, is_reply=True)
async def add_new_info(message: types.Message, user: User, reply: types.Message):
    try:
        thread = await get_thread(reply.message_id)
    except DoesNotExist:
        logger.info(
            "admin {user} send message as reply but without thread",
            user=user.id
        )
        return await message.reply(
            "It's unclear, this message is not directed to the start message",
            protect_content=False,
        )

    try:
        a_t, workers = await add_info_to_thread(message.html_text, thread=thread)
    except ThreadStopped:
        return await message.reply("This match is over!", protect_content=False)
    except Exception:
        logger.info("admin {user} try add new info to thread {thread} but failed",
                    user=user.id, thread=thread.id)
        await message.reply(
            "Something went wrong, I'm sure one day things thing will get back to normal, "
            "for now I can only suggest you to send it again",
            protect_content=False,
        )
        raise
    logger.info("admin {user} add new info {a_t} to thread {thread} ",
                user=user.id, a_t=a_t.id, thread=thread.id)
    await message.reply(
        f"Send information:\n{a_t.text}",
        reply_markup=kb.get_kb_menu_send(workers, a_t),
        protect_content=False,
    )


async def get_additional_text(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    additional_text_id = int(callback_data['additional_text'])
    try:
        a_t = await AdditionalText.get(id=additional_text_id)
        thread = await a_t.thread
        if thread.stopped:
            raise DoesNotExist
    except DoesNotExist:
        logger.info("admin {user} try send message without thread", user=user.id)
        await callback_query.answer(
            "This is some kind of strange button, I'll take it out of harm's way",
            show_alert=True,
        )
        await callback_query.message.edit_text(
            "There was some old message with invalid buttons",
        )
        raise CancelHandler
    else:
        return a_t, thread


@dp.callback_query_handler(kb.cb_send_now.filter())
async def send_new_info_now(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)
    asyncio.create_task(
        process_mailing(callback_query, a_t, callback_query.bot, thread=thread)
    )


async def process_mailing(callback_query: types.CallbackQuery, a_text: AdditionalText, bot: Bot, thread: WorkThread):
    logger.info("start sending additional info {a_t}", a_t=a_text.id)
    try:
        await start_mailing(a_text, bot, thread=thread)
    except ThreadStopped:
        return await callback_query.answer("This match is over!", show_alert=True)
    except Exception:
        await callback_query.answer(
            "An error occurred, we wrote it down, we will try to figure it out",
            show_alert=True
        )
        raise
    await callback_query.message.edit_text(f"Sent by:\n{a_text.text}")


@dp.callback_query_handler(kb.cb_update.filter())
async def update_handler(
        callback_query: types.CallbackQuery,
        callback_data: typing.Dict[str, str],
        user: User
):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)

    logger.info(
        "admin {user} update send menu for thread {thread}",
        user=user.id, thread=thread.id
    )
    try:
        await callback_query.message.edit_reply_markup(
            kb.get_kb_menu_send(await get_workers(a_t), a_t)
        )
    except MessageNotModified:
        await callback_query.answer("Already updated", cache_time=3)


@dp.callback_query_handler(kb.cb_is_disinformation.filter())
async def change_disinformation_handler(
        callback_query: types.CallbackQuery,
        callback_data: typing.Dict[str, str],
        user: User
):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)

    is_disinformation = bool(int(callback_data['is_disinformation']))
    logger.info(
        "admin {user} mark text as "
        "{disinformation}disinformation in thread {thread}",
        user=user.id,
        thread=thread.id,
        disinformation="" if is_disinformation else "not ",
    )
    await change_disinformation(a_t, is_disinformation)
    await callback_query.message.edit_reply_markup(
        kb.get_kb_menu_send(await get_workers(a_t), a_t)
    )


@dp.callback_query_handler(kb.cb_workers.filter())
async def change_addressee_workers(
        callback_query: types.CallbackQuery,
        callback_data: typing.Dict[str, str],
        user: User
):
    a_t, thread = await get_additional_text(callback_query, callback_data, user)
    worker_id = int(callback_data["send_worker_id"])
    enable = bool(int(callback_data["enable"]))
    await change_worker(worker_id, enable)

    logger.info(
        "admin {user} {change} text info {a_t} for worker {worker} in {thread}",
        user=user.id,
        change="enable" if enable else "disable",
        a_t=a_t.id,
        worker=worker_id,
        thread=thread.id,
    )
    await callback_query.message.edit_reply_markup(
        kb.get_kb_menu_send(await get_workers(a_t), a_t)
    )


@dp.callback_query_handler(kb.cb_stop.filter(), is_admin=True)
async def stop_work_thread(
        callback_query: types.CallbackQuery,
        callback_data: typing.Dict[str, str]
):
    thread_id = int(callback_data['thread_id'])
    try:
        thread = await stop_thread(thread_id)
    except DoesNotExist:
        await thread_not_found(callback_query, thread_id)
        return
    logger.info(
        "thread {thread_id} closed successfully by admin {admin}",
        thread_id=thread.id,
        admin=callback_query.from_user.id
    )
    await callback_query.answer()
    caption = (
        f"{thread.id}. "
        f"Match {thread.name if thread.name is not None else ''} "
        f"has been successfully finished"
    )
    try:
        # edit message in PM admin
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=kb.get_stopped_work_thread_admin_kb(thread_id),
        )
    except BadRequest as e:
        logger.exception(e)

    try:
        # edit message in workers chat
        await callback_query.bot.edit_message_caption(
            chat_id=config.WORKERS_CHAT_ID,
            message_id=thread.workers_chat_message_id,
            caption=caption,
            reply_markup=None,
        )
    except BadRequest as e:
        logger.exception(e)
    await send_notification_stop(thread, callback_query.bot)


@dp.callback_query_handler(kb.cb_rename_thread.filter(), is_admin=True)
async def start_rename_thread_process(
        callback_query: types.CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext
):
    await callback_query.answer()
    thread_id = int(callback_data['thread_id'])
    await state.update_data(thread_id=thread_id)
    await RenameThread.name.set()
    await callback_query.message.answer("Send a new name for this match")


@dp.message_handler(is_admin=True, state=RenameThread.name)
async def save_new_name_process(message: types.Message, state: FSMContext):
    await rename_thread((await state.get_data())['thread_id'], message.text)
    await state.finish()
    await message.reply("Saved!")
