import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation, Unauthorized
from loguru import logger
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.config.currency import Currency
from app.misc import dp
from app import config
from app import keyboards as kb
from app.services.text_utils import parse_numeric
from app.services.work_threads import thread_not_found
from app.models import User, WorkThread, Bookmaker
from app.services.remove_message import delete_message
from app.services.workers import add_worker_to_thread
from app.services.bets_log import save_new_betting_odd


class Report(StatesGroup):
    bet = State()
    result = State()
    bookmaker = State()
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
async def start_fill_report(
        callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    await callback_query.answer()
    await state.update_data(thread_id=int(callback_data["thread_id"]))
    await callback_query.message.reply(
        "Выберите валюту сделанной ставки",
        reply_markup=kb.get_kb_currency(config.currencies)
    )


@dp.callback_query_handler(kb.cb_currency.filter(), is_admin=False, chat_type=types.ChatType.PRIVATE)
async def process_currency_in_report(
        callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    await callback_query.answer()
    await state.update_data(currency=callback_data['code'])
    await callback_query.message.edit_text(
        f"Выбрана валюта {config.currencies[callback_data['code']]}"
    )
    await Report.bet.set()
    await callback_query.message.reply("Введите ставку:")


@dp.message_handler(is_admin=False, chat_type=types.ChatType.PRIVATE, state=Report.bet)
async def process_bet_in_report(message: types.Message, state: FSMContext):
    try:
        bet = parse_numeric(message.text)
    except ValueError:
        return await message.reply("Это явно не число.")
    await state.update_data(bet=bet)
    await Report.next()
    await message.answer("Введите расчёт:")


@dp.message_handler(is_admin=False, chat_type=types.ChatType.PRIVATE, state=Report.result)
async def process_result_in_report(message: types.Message, state: FSMContext):
    try:
        result = parse_numeric(message.text)
    except ValueError:
        return await message.reply("Это явно не число.")
    await state.update_data(result=result)
    await Report.next()
    await message.answer("Введите букмекера:")


@dp.message_handler(is_admin=False, chat_type=types.ChatType.PRIVATE, state=Report.bookmaker)
async def process_result_in_report(message: types.Message, state: FSMContext):
    try:
        bookmaker = await Bookmaker.get(name=message.text)
    except DoesNotExist:
        await state.update_data(new_bookmaker=message.text)
        return await message.reply(
            "Этот букмекер мне не известен, уверены, что хотите добавить нового?",
            reply_markup=kb.get_kb_confirm_add_bookmaker(),
        )
    await state.update_data(bookmaker_id=bookmaker.id)
    await Report.next()
    await send_check_data(message, state)


@dp.callback_query_handler(
    kb.cb_confirm_add_bookmaker.filter(yes=str(True)),
    is_admin=False,
    chat_type=types.ChatType.PRIVATE,
    state=Report.bookmaker
)
async def add_new_bookmaker(callback_query: types.CallbackQuery, state: FSMContext, user: User):
    state_data = await state.get_data()
    try:
        bookmaker = await Bookmaker.create(
            name=state_data.pop('new_bookmaker'),
            add_by=user,
        )
        await state.set_data(state_data)
        await callback_query.message.edit_text("Букмекер успешно добавлен")
    except IntegrityError:
        bookmaker = await Bookmaker.get(name=state_data['new_bookmaker'])
        await callback_query.message.edit_text("Букмекер был добавлен только что кем-то ещё")
    await state.update_data(bookmaker_id=bookmaker.id)
    await Report.next()
    await send_check_data(callback_query.message, state)


@dp.callback_query_handler(
    kb.cb_confirm_add_bookmaker.filter(yes=str(False)),
    is_admin=False,
    chat_type=types.ChatType.PRIVATE,
    state=Report.bookmaker
)
async def add_new_bookmaker(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    state_data.pop('new_bookmaker')
    await state.set_data(state_data)
    await callback_query.message.edit_text(
        "Вы отказались добавлять нового букмекера.\nВведите букмекера."
    )


async def send_check_data(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    current_currency_symbol = config.currencies[state_data['currency']].symbol
    bookmaker = await Bookmaker.get(id=state_data['bookmaker_id'])
    await message.answer(
        "<b>Всё верно?</b>\n\n"
        f"Букмекер {bookmaker.name}\n"
        f"Сделана ставка: {state_data['bet']} {current_currency_symbol}\n"
        f"Расчёт: {state_data['result']} {current_currency_symbol}\n",
        reply_markup=kb.get_kb_confirm_report(),
    )


@dp.callback_query_handler(
    kb.cb_confirm_report.filter(yes=str(True)),
    is_admin=False,
    chat_type=types.ChatType.PRIVATE,
    state=Report.ok
)
async def saving(callback_query: types.CallbackQuery, state: FSMContext, user: User):
    try:
        state_data = await state.get_data()
        currency: Currency = config.currencies[state_data.pop('currency')]
        betting_item = await save_new_betting_odd(user=user, bot=callback_query.bot, currency=currency, **state_data)

        await callback_query.message.edit_text(f"Успешно сохранено\n{betting_item}")
        await state.finish()
        await callback_query.answer()
    except Exception:
        await callback_query.answer("Произошла ошибка", show_alert=True)
        raise


@dp.callback_query_handler(
    kb.cb_confirm_report.filter(yes=str(False)),
    is_admin=False,
    chat_type=types.ChatType.PRIVATE,
    state=Report.ok
)
async def saving(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Сохранение отменено", show_alert=True)
    await callback_query.message.edit_text("Сохранение отменено")
    await state.finish()
