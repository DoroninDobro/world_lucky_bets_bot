
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, SwitchTo, Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.panel.getters import get_users, get_user, get_salary_types, get_selected_salary_type
from app.dialogs.panel.handlers import select_user, add_transaction_start, select_salary_type, input_salary, \
    unregister_user
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
            Const("Remove from list"),
            state=Panel.remove_user,
            id="remove_user",
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
        Format("Remove {user}\n<b>Are you sure?</b>"),
        Button(
            Const("Remove"),
            on_click=unregister_user,
            id="remove_user",
        ),
        SwitchTo(
            Const("No! Cancel!"),
            state=Panel.user_main,
            id="to_user",
        ),
        getter=get_user,
        state=Panel.remove_user,
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
    Window(
        Format(
            "Enter value for selected salary type {salary_type.name} "
            "for user {user.mention_link}"
        ),
        SwitchTo(
            Const("Go to main"),
            id="to_users",
            state=Panel.users,
        ),
        MessageInput(func=input_salary),
        getter=get_selected_salary_type,
        state=Panel.change_salary_value,
    ),
)
