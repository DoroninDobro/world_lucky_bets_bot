from aiogram import types
from aiogram.dispatcher.handler import SkipHandler

from app import config
from app.misc import dp


@dp.channel_post_handler(chat_id=config.WORKERS_CHAT_ID)
async def forwarding_all(message: types.Message):
    await message.forward(config.ADMINS_WITHOUT_USERNAMES_LOG_CHAT_ID)
    raise SkipHandler
