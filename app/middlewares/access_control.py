import typing

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger


class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, allow_list: typing.Iterable):
        super().__init__()
        self.allow_list = allow_list

    async def on_pre_process_update(self, update: types.Update, _: dict):
        try:
            user = get_update_user(update)
        except AttributeError:
            return logger.debug(f"event don't have user in update {update}")

        if user.id not in self.allow_list:
            logger.debug("access for user {user} deny", user=user.id)
            raise CancelHandler
        logger.debug("access for user {user} allow", user=user.id)


def get_update_user(update: types.Update):
    event = update.message \
        or update.edited_message \
        or update.callback_query \
        or update.inline_query \
        or update.chosen_inline_result \
        or update.shipping_query \
        or update.pre_checkout_query
    return event.from_user
