from typing import Any

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from app.models.enum.user_status import WorkerStatus
from app.view.keyboards import balance as kb_balance
from app.states import Panel, AddTransaction


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


async def add_transaction_start(c: CallbackQuery, button: Any, manager: DialogManager):
    await c.answer()
    state: FSMContext = manager.data["state"]
    await state.set_state(AddTransaction.sign)
    await state.update_data(
        user_id=manager.current_context().dialog_data["active_user"],
        author_id=manager.data["user"].id,
    )
    await c.message.answer(
        text="Please select type of transaction:",
        reply_markup=kb_balance.get_transaction_sign(),
    )


async def select_salary_type(c: CallbackQuery, widget: Any, manager: DialogManager, item_id):
    await c.answer()
    data = manager.current_context().start_data
    if not isinstance(data, dict):
        data = {}
    data["salary_type"] = WorkerStatus[item_id].name
    await manager.update(data)
    await manager.switch_to(Panel.change_salary_value)
