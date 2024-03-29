# partially from https://github.com/aiogram/bot

from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.models.config import Config
from app.models.db.chat import Chat
from app.models.db.user import User
from app.services.rates import OpenExchangeRates
from app.utils.lock_factory import LockFactory


class DbMiddleware(BaseMiddleware):
    def __init__(self, config: Config, oer: OpenExchangeRates):
        super(DbMiddleware, self).__init__()
        self.lock_factory = LockFactory()
        self.config = config
        self.oer = oer

    async def setup_chat(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):
        async with self.lock_factory.get_lock(f"{user.id}"):
            user = await User.get_or_create_from_tg_user(user)
        async with self.lock_factory.get_lock(f"{chat.id}"):
            chat = await Chat.get_or_create_from_tg_chat(chat)

        data["user"] = user
        data["chat"] = chat
        data["config"] = self.config
        data["oer"] = self.oer

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)

    async def on_pre_process_channel_post(self, channel_post: types.Message, data: dict):
        async with self.lock_factory.get_lock(f"{channel_post.chat.id}"):
            chat = await Chat.get_or_create_from_tg_chat(channel_post.chat)
        data["chat"] = chat
        data["config"] = self.config
        data["oer"] = self.oer

