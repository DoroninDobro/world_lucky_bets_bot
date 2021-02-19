# partially from https://github.com/aiogram/bot
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor
from loguru import logger

from app import config
from app.config import DBConfig
from app.misc import dp
from app.models.db import db

runner = Executor(dp)


async def on_startup_webhook(dispatcher: Dispatcher):
    webhook_url = f'{config.WEBHOOK_URL_BASE}{config.secret_str}/'
    logger.info("Configure Web-Hook URL to: {url}", url=webhook_url)
    await dispatcher.bot.set_webhook(webhook_url)


async def on_startup_notify(dispatcher: Dispatcher):
    with suppress(TelegramAPIError):
        await dispatcher.bot.send_message(
            chat_id=config.TECH_LOG_CHAT_ID, text="Bot started", disable_notification=True
        )
        logger.info("Notified superusers about bot is started.")
    # await send_log_files(config.LOG_CHAT_ID)


def setup(db_config: DBConfig):
    logger.info("Configure executor...")
    db.setup(runner, db_config)
    runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    runner.on_startup(on_startup_notify)
