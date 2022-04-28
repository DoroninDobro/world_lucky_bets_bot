from typing import Any

from aiogram_dialog import DialogManager

from app.models import User
from app.services.balance import calculate_balance
from app.services.rates import OpenExchangeRates
from app.services.workers import get_registered


async def get_users(**kwargs):
    return {
        "users": await get_registered(),
    }


async def get_user(dialog_manager: DialogManager, **kwargs):
    data: dict[str, Any] = dialog_manager.current_context().dialog_data
    config = dialog_manager.data["config"]
    user = await User.get(id=data["active_user"])
    async with OpenExchangeRates(api_key=config.currencies.oer_api_token) as oer:
        return {
            "user": user,
            "balance": await calculate_balance(user, oer=oer, config=config.currencies),
        }

