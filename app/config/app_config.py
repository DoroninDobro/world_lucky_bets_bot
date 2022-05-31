from typing import Any

from app.models.config.app_config import AppConfig, ChatsConfig


def load_app_config(dct: dict[str, Any]) -> AppConfig:
    return AppConfig(
        admins=set(dct["admins"]),
        chats=load_chats(dct["chats"]),
    )


def load_chats(dct: dict[str, Any]) -> ChatsConfig:
    return ChatsConfig(
        tech_log=dct["tech_log"],
        user_log=dct["user_log"],
        admin_log=dct["admin_log"],
        workers=dct["workers"],
        admins_without_usernames_log=dct["admins_without_usernames_log"],
    )
