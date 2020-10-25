from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from app import config
from app.models import User


@dataclass
class IsAdminFilter(BoundFilter):
    key = "is_admin"
    is_admin: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        user: User = data["user"]
        return (user.id in config.admins_list) == self.is_admin
