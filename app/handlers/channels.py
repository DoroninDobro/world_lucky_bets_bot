from aiogram import types
from aiogram.dispatcher.handler import SkipHandler

from app import config
from app.misc import dp
from app.utils.text_utils import remove_usernames


@dp.channel_post_handler(chat_id=config.WORKERS_CHAT_ID)
async def forwarding_all(message: types.Message):
    await message.bot.send_message(
        config.ADMINS_WITHOUT_USERNAMES_LOG_CHAT_ID,
        remove_usernames(message.html_text),
    )
    raise SkipHandler
