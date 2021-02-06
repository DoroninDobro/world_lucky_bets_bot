from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hpre, hbold
from loguru import logger

from app.misc import dp
from app.models.db.chat import Chat


@dp.message_handler(commands=["start"], commands_prefix='!/', is_admin=False)
@dp.throttled(rate=3)
async def cmd_start(message: types.Message):
    """For start handler for admin see admin.py """
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.reply(
        "Привет "
    )


@dp.message_handler(commands=["help"], commands_prefix='!/')
@dp.throttled(rate=3)
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    await message.reply(
        'Здесь будет помощь'
    )


@dp.message_handler(commands='idchat', commands_prefix='!/')
@dp.throttled(rate=30)
async def get_idchat(message: types.Message):
    text = (
        f"id этого чата: {hpre(message.chat.id)}\n"
        f"Ваш id: {hpre(message.from_user.id)}"
    )
    if message.reply_to_message:
        text += (
            f"\nid {hbold(message.reply_to_message.from_user.full_name)}: "
            f"{hpre(message.reply_to_message.from_user.id)}"
        )
    await message.reply(text, disable_notification=True)


@dp.message_handler(state='*', commands='cancel')
@dp.throttled(rate=3)
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info(f'Cancelling state {current_state}')
    await state.finish()
    await message.reply(
        'Введённые во время диалога данные удалены, а сам диалог прекращён',
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(content_types=types.ContentTypes.MIGRATE_TO_CHAT_ID)
async def chat_migrate(message: types.Message, chat: Chat):
    old_id = message.chat.id
    new_id = message.migrate_to_chat_id
    chat.chat_id = new_id
    await chat.save()
    logger.info(f"Migrate chat from {old_id} to {new_id}")
