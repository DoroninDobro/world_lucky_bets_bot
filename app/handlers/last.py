from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.handler import SkipHandler
from loguru import logger

from app.misc import dp

YOU_ARE_IN_STATE_MSG = "You are in the dialogue (eg sending the data for the report). " \
    "If you do not remember this or do not understand what it is about - press /cancel"


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['.*']), state='*')
async def message_in_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        raise SkipHandler
    logger.info(
        'user {user} with {current_state} in {chat} send command {command}',
        current_state=current_state,
        user=message.from_user.id,
        chat=message.chat.id,
        command=message.get_command()
    )
    await message.reply(YOU_ARE_IN_STATE_MSG)


@dp.callback_query_handler()
async def not_supported_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(
        "This button is not supported or intended for you. I don't know where you got it",
        show_alert=True
    )
    logger.warning(
        "User {user} press unsupported button in query {query}",
        user=callback_query.from_user.id,
        query=callback_query.as_json()
    )


@dp.callback_query_handler(state='*')
async def not_supported_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(YOU_ARE_IN_STATE_MSG)
    await callback_query.message.answer(YOU_ARE_IN_STATE_MSG)
