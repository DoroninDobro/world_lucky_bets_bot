from aiogram_dialog import DialogRegistry

from .dialog import panel


def setup_dialogs(registry: DialogRegistry):
    registry.register(panel)
