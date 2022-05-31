# partially from https://github.com/aiogram/bot
from contextlib import suppress
from functools import partial

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor
from loguru import logger

from app.constants import WEBHOOK_URL_BASE, secret_str
from app.misc import dp
from app.models.config import Config
from app.models.db import db

runner = Executor(dp)


async def on_startup_webhook(dispatcher: Dispatcher):
    webhook_url = f'{WEBHOOK_URL_BASE}{secret_str}/'
    logger.info("Configure Web-Hook URL to: {url}", url=webhook_url)
    await dispatcher.bot.set_webhook(webhook_url)


async def on_startup_notify(dispatcher: Dispatcher, config: Config):
    with suppress(TelegramAPIError):
        await dispatcher.bot.send_message(
            chat_id=config.app.chats.tech_log, text="Bot started", disable_notification=True
        )
        logger.info("Notified superusers about bot is started.")


def setup(config: Config):
    logger.info("Configure executor...")
    db.setup(runner, config.db)
    runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    runner.on_startup(partial(on_startup_notify, config=config))
