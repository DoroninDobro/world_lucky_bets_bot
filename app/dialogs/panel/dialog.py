
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.panel.getters import get_users
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
            ),
            id="users_sg",
            width=1,
            height=10,
        ),
        getter=get_users,
        state=Panel.users,
    )
)
