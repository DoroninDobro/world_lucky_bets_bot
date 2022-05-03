from decimal import Decimal

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext

from app.misc import dp
from app.models import User
from app.models.config import Config
from app.models.data.transaction import TransactionData
from app.services.balance import add_balance_event
from app.states import AddTransaction
from app.view.keyboards import balance as kb_balance


@dp.message_handler(commands="transaction", is_admin=False, chat_type=types.ChatType.PRIVATE)
async def add_transaction_start(message: types.Message, state: FSMContext, user: User):
    await state.set_state(AddTransaction.sign)
    await state.update_data(user_id=user.id, author_id=user.id)
    await message.answer(
        text="Please select type of transaction:",
        reply_markup=kb_balance.get_transaction_sign(),
    )


@dp.message_handler(commands="transaction", is_admin=True)
async def add_transaction_start(message: types.Message):
    await message.answer(
        text="You are an admin. This command only for workers.",
    )


@dp.callback_query_handler(kb_balance.cb_sign.filter(), state=AddTransaction.sign)
async def save_sign(
        callback_query: types.CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
        config: Config,
):
    sign = callback_data["sign"]
    if sign not in kb_balance.SIGNS:
        raise RuntimeError(f"unknown cb_data {callback_data} contains {sign}")
    await callback_query.answer()
    is_income = sign == kb_balance.INCOME
    await state.update_data(is_income=is_income)
    await state.set_state(AddTransaction.currency)
    await callback_query.message.edit_text(
        text="Please select the currency",
        reply_markup=kb_balance.get_kb_currency(currencies=config.currencies.currencies),
    )


@dp.callback_query_handler(kb_balance.cb_currency.filter(), state=AddTransaction.currency)
async def save_currency(
        callback_query: types.CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
):
    currency = callback_data["code"]
    await state.update_data(iso_code=currency)
    await state.set_state(AddTransaction.amount)
    await callback_query.answer()
    await callback_query.message.answer(text="Please, enter amount:")
    data = await state.get_data()
    await callback_query.message.edit_text(
        f"Type of transaction: [{list(kb_balance.SIGNS.values())[int(not data['is_income'])]}]\n"
        f"The currency: [{currency}]"
    )


@dp.message_handler(state=AddTransaction.amount)
async def save_amount(message: types.Message, state: FSMContext):
    try:
        amount = Decimal(message.text)
    except ValueError:
        return await message.reply(text="sorry but it is not correct value")
    await state.update_data(amount=amount)
    await state.set_state(AddTransaction.comment)
    await message.reply(
        text="Enter a comment if you have one. Else click complete",
        reply_markup=kb_balance.get_kb_complete(),
    )


@dp.message_handler(state=AddTransaction.comment)
async def save_with_comment(message: types.Message, state: FSMContext, config: Config):
    comment = message.text
    await save_transaction(state, config, message.bot, comment)
    await message.answer("Saved!")


@dp.callback_query_handler(kb_balance.cb_complete.filter(), state=AddTransaction.comment)
async def save_without_comment(callback_query: types.CallbackQuery, state: FSMContext, config: Config):
    await callback_query.answer()
    await save_transaction(state, config, callback_query.bot)
    await callback_query.message.edit_text("Have no comments for this transaction")


async def save_transaction(state: FSMContext, config: Config, bot: Bot, comment: str = ""):
    saved_data = await state.get_data()
    transaction_data = TransactionData(
        user_id=saved_data["user_id"],
        author_id=saved_data["author_id"],
        is_income=bool(saved_data["is_income"]),
        currency=config.currencies.currencies[saved_data["iso_code"]],
        amount=Decimal(saved_data["amount"]),
        comment=comment,
    )
    await add_balance_event(transaction_data)
    await bot.send_message(
        config.app.chats.user_log,
        text=str(transaction_data),
    )
    await state.finish()

