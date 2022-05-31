from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AppConfig:
    admins: set[int]
    chats: ChatsConfig


@dataclass
class ChatsConfig:
    tech_log: int
    user_log: int
    admin_log: int
    workers: int
    admins_without_usernames_log: int
