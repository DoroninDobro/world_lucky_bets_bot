from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from app import config
from app.models import Chat


@dataclass
class IsAdminFilter(BoundFilter):
    key = "is_admin"
    is_admin: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        chat: Chat = data["chat"]
        return (chat.id in config.admins_list) == self.is_admin
