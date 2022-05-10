from typing import Any

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from app.models.db import User
from app.models.enum.salary_type import SalaryType
from app.models.enum.blance_event_type import BalanceEventType
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
        balance_event_type=BalanceEventType.ADMIN.name,
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
    data["salary_type"] = SalaryType[item_id].name
    await manager.update(data)
    await manager.switch_to(Panel.change_salary_value)


async def input_salary(m: Message, _, manager: DialogManager):
    dialog_data = manager.current_context().dialog_data
    salary_type = SalaryType[dialog_data["salary_type"]]
    user = await User.get(id=dialog_data["active_user"])
    user.worker_status = salary_type
    if salary_type == SalaryType.SALARY:
        user.salary = m.text
    else:
        try:
            piecework_pay = int(m.text)
        except ValueError:
            return await m.answer("it is not a valid value")
        if piecework_pay < 0 or piecework_pay > 100:
            return await m.answer("value must be greater that 0 and less of 100")
        user.piecework_pay = piecework_pay
    await user.save()
    await manager.switch_to(Panel.user_main)


