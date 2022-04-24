from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from app.states import Panel


async def select_user(
        c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str,
):
    await c.answer()
    data = manager.current_context().start_data
    if not isinstance(data, dict):
        data = {}
    data["active_user"] = int(item_id)
    await manager.update(data)
    await manager.switch_to(Panel.user_main)
