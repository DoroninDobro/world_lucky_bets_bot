from typing import Any

from aiogram_dialog import DialogManager

from app.models import User
from app.services.workers import get_registered


async def get_users(**kwargs):
    return {
        "users": await get_registered(),
    }


async def get_user(dialog_manager: DialogManager, **kwargs):
    data: dict[str, Any] = dialog_manager.current_context().dialog_data
    return {"user": await User.get(id=data["active_user"])}

