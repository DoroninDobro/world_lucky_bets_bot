import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation, Unauthorized
from loguru import logger
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.misc import dp
from app import config
from app import keyboards as kb
from app.services.text_utils import parse_numeric_float
from app.services.work_threads import thread_not_found
from app.models import User, WorkThread
from app.services.remove_message import delete_message
from app.services.workers import add_worker_to_thread


class Report(StatesGroup):
    bet = State()
    result = State()
    ok = State()


@dp.callback_query_handler(kb.cb_agree.filter(), is_admin=False)
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
            caption=f"{thread_id}. Вы подписаны на это",
            reply_markup=kb.get_kb_send_report(user, thread)
        )
    except (BotBlocked, CantInitiateConversation, Unauthorized):
        logger.info("user {user} try to be worker in thread {thread} but he don't start conversation with bot",
                    user=user.id, thread=thread_id)
        return await callback_query.answer("Сначала напишите мне что-то в личку", show_alert=True)

    try:
        await add_worker_to_thread(user, msg.message_id, msg.bot, thread=thread)
    except IntegrityError:
        await delete_message(msg)
        logger.info("user {user} try to be worker in thread {thread} but he already worker in that thread",
                    user=user.id, thread=thread_id)
        return await callback_query.answer("Ошибка, Вы уже подписаны?", show_alert=True, cache_time=3600)

    await callback_query.answer("успешно")
    logger.info("user {user} now worker in thread {thread}", user=user.id, thread=thread_id)


@dp.callback_query_handler(kb.cb_agree.filter())
async def agree_work_thread(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], user: User):
    await callback_query.answer("Админ не может участвовать в работе!", show_alert=True, cache_time=3600)
    thread_id = int(callback_data['thread_id'])
    logger.info("admin {user}, try to be worker in thread {thread}", user=user.id, thread=thread_id)


@dp.callback_query_handler(kb.cb_send_report.filter(), is_admin=False, chat_type=types.ChatType.PRIVATE)
async def start_fill_report(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    await state.update_data(thread_id=int(callback_data["thread_id"]))
    await callback_query.message.reply(
        "Выберите валюту сделанной ставки",
        reply_markup=kb.get_kb_currency(config.currencies)
    )


@dp.callback_query_handler(kb.cb_currency.filter(), is_admin=False, chat_type=types.ChatType.PRIVATE)
async def process_currency_in_report(
        callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    await state.update_data(currency=callback_data['code'])
    await callback_query.message.edit_text(
        f"Выбрана валюта {config.currencies[callback_data['code']]}"
    )
    await Report.bet.set()
    await callback_query.message.reply("Введите ставку:")


@dp.message_handler(is_admin=False, chat_type=types.ChatType.PRIVATE, state=Report.bet)
async def save_bet(message: types.Message, state: FSMContext):
    try:
        bet = parse_numeric_float(message.text)
    except ValueError:
        return await message.reply("Это явно не число.")
    await state.update_data(bet=bet)
    await Report.next()
    await message.answer("Введите результ:")


@dp.message_handler(is_admin=False, chat_type=types.ChatType.PRIVATE, state=Report.result)
async def save_result(message: types.Message, state: FSMContext):
    try:
        result = parse_numeric_float(message.text)
    except ValueError:
        return await message.reply("Это явно не число.")
    await state.update_data(result=result)
    await Report.next()
    await message.answer(
        "всё верно?",
        #  TODO клава
    )


@dp.message_handler(is_admin=False, chat_type=types.ChatType.PRIVATE, state=Report.ok)
async def check_before_saving(message: types.Message, state: FSMContext):
    pass
