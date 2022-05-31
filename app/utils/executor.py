# partially from https://github.com/aiogram/bot
import asyncio
from contextlib import suppress
from functools import partial

from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from aiogram.utils.exceptions import TelegramAPIError, BadRequest
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


async def set_commands(dispatcher: Dispatcher, chats: set[int]):
    await dispatcher.bot.set_my_commands(
        [
            BotCommand("start", "start bot"),
            BotCommand("registration", "registration in users"),
            BotCommand("transaction", "add a new transaction"),
            BotCommand("status", "my balance and salary"),
        ],
        scope=BotCommandScopeDefault(),
    )
    for chat_id in chats:
        with suppress(BadRequest):
            await asyncio.sleep(0.3)
            await dispatcher.bot.set_my_commands(
                [
                    BotCommand("start", "start bot"),
                    BotCommand("users", "get list of users"),
                ],
                scope=BotCommandScopeChat(chat_id=chat_id),
            )


def setup(config: Config):
    logger.info("Configure executor...")
    db.setup(runner, config.db)
    runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    runner.on_startup(partial(on_startup_notify, config=config))
    runner.on_startup(partial(set_commands, chats=config.app.admins))
