
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, SwitchTo, Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.panel.getters import get_users, get_user, get_salary_types
from app.dialogs.panel.handlers import select_user, add_transaction_start, select_salary_type
from app.states import Panel

panel = Dialog(
    Window(
        Const("Users list"),
        ScrollingGroup(
            Select(
                Format("{item.fullname}"),
                id="users",
                item_id_getter=lambda x: x.id,
                items="users",
                on_click=select_user
            ),
            id="users_sg",
            width=1,
            height=10,
        ),
        getter=get_users,
        state=Panel.users,
    ),
    Window(
        Format(
            "{user}\n"
            "balance: {balance}\n"
            "salary: {user.render_salary}\n"
            "Last transactions:\n"
            "{transactions}"
        ),
        Button(
            Const("Add transaction"),
            on_click=add_transaction_start,
            id="add_transaction",
        ),
        SwitchTo(
            Const("Change salary"),
            state=Panel.change_salary,
            id="change_salary"
        ),
        SwitchTo(
            Const("Back to users"),
            state=Panel.users,
            id="to_users_list",
        ),
        getter=get_user,
        state=Panel.user_main,
    ),
    Window(
        Format("select type of salary for {user}:"),
        Select(
            Format("{item.value}"),
            id="salary_types",
            item_id_getter=lambda x: x.name,
            items="salary_types",
            on_click=select_salary_type,
        ),
        getter=get_salary_types,
        state=Panel.change_salary,
    ),
)
