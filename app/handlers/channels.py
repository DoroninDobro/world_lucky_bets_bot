from aiogram import types
from aiogram.dispatcher.handler import SkipHandler

from app.misc import config as global_config
from app.misc import dp
from app.models.config import Config
from app.utils.text_utils import remove_usernames


@dp.channel_post_handler(chat_id=global_config.app.chats.workers)
async def forwarding_all(message: types.Message, config: Config):
    await message.bot.send_message(
        config.app.chats.admins_without_usernames_log,
        remove_usernames(message.html_text),
    )
    raise SkipHandler
