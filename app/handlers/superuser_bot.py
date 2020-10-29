from aiogram import types

from app import config
from app.misc import bot, dp
from app.utils.send_text_file import send_log_files


@dp.message_handler(is_superuser=True, commands='update_log')
@dp.throttled(rate=30)
@dp.async_task
async def get_log(_: types.Message):
    await send_log_files(bot, config.TECH_LOG_CHAT_ID)


@dp.message_handler(is_superuser=True, commands='logchat')
@dp.throttled(rate=30)
async def get_logchat(message: types.Message):
    log_ch = await bot.get_chat(config.TECH_LOG_CHAT_ID)
    await message.reply(log_ch.invite_link, disable_notification=True)


@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
@dp.throttled(rate=120)
async def generate_logchat_link(message: types.Message):
    await message.reply(await bot.export_chat_invite_link(config.TECH_LOG_CHAT_ID), disable_notification=True)


@dp.message_handler(is_superuser=True, commands=["exception"])
@dp.throttled(rate=30)
async def cmd_exception(_: types.Message):
    raise Exception('user press /exception')
