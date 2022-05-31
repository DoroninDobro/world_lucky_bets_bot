import asyncio
from contextlib import suppress

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.utils.exceptions import BadRequest


REGISTRATION_COMMAND = BotCommand("registration", "registration in users")
START_COMMAND = BotCommand("start", "start bot")
USERS_COMMAND = BotCommand("users", "get list of users")
STATUS_COMMAND = BotCommand("status", "my balance and salary")
TRANSACTION_COMMAND = BotCommand("transaction", "add a new transaction")


async def set_commands(bot: Bot, admins: set[int]):
    await bot.set_my_commands(
        [
            START_COMMAND,
            REGISTRATION_COMMAND,
            TRANSACTION_COMMAND,
            STATUS_COMMAND,
        ],
        scope=BotCommandScopeDefault(),
    )
    for chat_id in admins:
        with suppress(BadRequest):
            await asyncio.sleep(0.3)
            await bot.set_my_commands(
                [
                    START_COMMAND,
                    USERS_COMMAND,
                ],
                scope=BotCommandScopeChat(chat_id=chat_id),
            )
