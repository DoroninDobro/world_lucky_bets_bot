# partially from https://github.com/aiogram/bot
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor

from app import config
from app.config import DBConfig
from app.misc import dp
from app.models.db import db

runner = Executor(dp)


async def on_startup_webhook(dispatcher: Dispatcher):
    webhook_url = f'{config.WEBHOOK_URL_BASE}{config.secret_str}/'
    await dispatcher.bot.set_webhook(webhook_url)


async def on_startup_notify(dispatcher: Dispatcher):
    with suppress(TelegramAPIError):
        await dispatcher.bot.send_message(
            chat_id=config.TECH_LOG_CHAT_ID, text="Bot started", disable_notification=True
        )


def setup(db_config: DBConfig):
    db.setup(runner, db_config)
    runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    runner.on_startup(on_startup_notify)
