from aiogram import types
from aiogram.types import Message

from app.misc import bot, dp
from app.models.config import Config
from app.utils.commands import set_commands
from app.utils.send_text_file import send_log_files


@dp.message_handler(is_superuser=True, commands='update_log')
@dp.throttled(rate=30)
@dp.async_task
async def get_log(_: types.Message, config: Config):
    await send_log_files(bot, config.app.chats.tech_log, config.log_path)


@dp.message_handler(is_superuser=True, commands='logchat')
@dp.throttled(rate=30)
async def get_logchat(message: types.Message, config: Config):
    log_ch = await bot.get_chat(config.app.chats.tech_log)
    await message.reply(log_ch.invite_link, disable_notification=True)


@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
@dp.throttled(rate=120)
async def generate_logchat_link(message: types.Message, config: Config):
    await message.reply(await bot.export_chat_invite_link(config.app.chats.tech_log), disable_notification=True)


@dp.message_handler(is_superuser=True, commands=["exception"])
@dp.throttled(rate=30)
async def cmd_exception(_: types.Message):
    raise Exception('user press /exception')


@dp.message_handler(is_superuser=True, commands="reload_commands")
async def reload_commands(m: Message, config: Config):
    await set_commands(m.bot, config.app.admins)
