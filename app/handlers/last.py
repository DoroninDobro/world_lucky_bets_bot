from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.handler import SkipHandler
from aiogram.utils.exceptions import TelegramAPIError

from app.misc import dp

YOU_ARE_IN_STATE_MSG = "You are in the dialogue (eg sending the data for the report). " \
    "If you do not remember this or do not understand what it is about - press /cancel"


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['.*']), state='*')
async def message_in_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        raise SkipHandler
    await message.reply(YOU_ARE_IN_STATE_MSG)


@dp.callback_query_handler()
async def not_supported_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(
        "This button is not supported or intended for you. I don't know where you got it",
        show_alert=True
    )


@dp.callback_query_handler(state='*')
async def not_supported_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(YOU_ARE_IN_STATE_MSG, show_alert=True)
    try:
        await callback_query.bot.send_message(callback_query.from_user.id, YOU_ARE_IN_STATE_MSG)
    except TelegramAPIError as e:
        pass
