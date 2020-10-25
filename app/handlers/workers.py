import typing

from aiogram import types
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation, Unauthorized
from loguru import logger
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.misc import dp

from . import keyboards as kb
from app.services.work_threads import (
     thread_not_found,
)
from app.models import User, WorkThread
from ..services.workers import add_worker_to_thread, get_worker_in_thread, get_bet_and_odd, save_new_betting_odd
from ..utils.exceptions import ThreadStopped


@dp.callback_query_handler(kb.cb_agree.filter(), is_admin=False)
@dp.throttled(rate=3)
async def agree_work_thread(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    thread_id = int(callback_data['thread_id'])
    try:
        thread = await WorkThread.get(id=thread_id)
        if thread.stopped:
            raise DoesNotExist
    except DoesNotExist:
        return await thread_not_found(callback_query, thread_id)

    try:
        msg = await callback_query.bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=thread.start_photo_file_id,
            caption="Вы подписаны на это"
        )
    except (BotBlocked, CantInitiateConversation, Unauthorized):
        return await callback_query.answer("Сначала напишите мне что-то в личку", show_alert=True)

    try:
        await add_worker_to_thread(user, thread, msg.message_id, msg.bot)
    except IntegrityError:
        await callback_query.answer("Ошибка, Вы уже подписаны?", show_alert=True, cache_time=3600)
    await callback_query.answer("успешно")


@dp.message_handler(is_admin=False, is_reply=True, chat_type=types.ChatType.PRIVATE)
@dp.throttled(rate=1)
async def new_send(message: types.Message, user: User, reply: types.Message):
    try:
        wit = await get_worker_in_thread(reply.message_id, user)
    except DoesNotExist:
        return await message.reply("Непонятно к чему этот реплай, но на всякий случай я ничего не понял.")

    try:
        betting_odd = get_bet_and_odd(message.text)
    except ValueError:
        return await message.reply("Это ставка? Мне не понятно. Я понимаю в формате \"200 1.5\"")

    try:
        await save_new_betting_odd(betting_odd, wit, message.bot)
    except ThreadStopped:
        await message.reply("Этот матч завершён")
    logger.info("worker {user} send new bet {bet}", user=message.from_user.id, bet=betting_odd)
    await message.reply(f"ставка {betting_odd} принята")


