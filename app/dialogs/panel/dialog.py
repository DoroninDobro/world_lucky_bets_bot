
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.panel.getters import get_users, get_user
from app.dialogs.panel.handlers import select_user
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
        Format("{user}\nbalance: {balance}"),
        SwitchTo(
            Const("Back to users"),
            state=Panel.users,
            id="to_users_list",
        ),
        getter=get_user,
        state=Panel.user_main,
    ),
)
