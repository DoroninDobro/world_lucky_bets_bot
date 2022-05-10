from typing import Any

from aiogram_dialog import DialogManager

from app.models.db import User
from app.models.config import Config
from app.models.enum.salary_type import SalaryType
from app.rendering.balance import render_balance
from app.services.balance import calculate_balance, get_last_balance_events
from app.services.rates import OpenExchangeRates
from app.services.workers import get_registered


async def get_users(**kwargs):
    return {
        "users": await get_registered(),
    }


async def get_user(dialog_manager: DialogManager, **kwargs):
    data: dict[str, Any] = dialog_manager.current_context().dialog_data
    config: Config = dialog_manager.data["config"]
    user = await User.get(id=data["active_user"])
    async with OpenExchangeRates(api_key=config.currencies.oer_api_token) as oer:
        return {
            "user": user,
            "balance": render_balance(
                balance=await calculate_balance(user, oer=oer, config=config.currencies),
                currency=config.currencies.default_currency,
            ),
            "transactions": "\n".join([
                await be.format() for be in await get_last_balance_events(user)
            ]),
        }


async def get_salary_types(dialog_manager: DialogManager, **kwargs):
    data: dict[str, Any] = dialog_manager.current_context().dialog_data
    user = await User.get(id=data["active_user"])
    return {
        "salary_types": [item for item in SalaryType],
        "user": user,
    }


async def get_selected_salary_type(dialog_manager: DialogManager, **kwargs):
    data: dict[str, Any] = dialog_manager.current_context().dialog_data
    user = await User.get(id=data["active_user"])
    return {
        "salary_type": SalaryType[data["salary_type"]],
        "user": user,
    }
