from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from dateutil import tz

from app.models.config.app_config import AppConfig
from app.models.config.currency import CurrenciesConfig
from app.models.config.db import DBConfig
from app.models.config.storage import StorageConfig


@dataclass
class Config:
    paths: Paths
    db: DBConfig
    bot: BotConfig
    storage: StorageConfig
    currencies: CurrenciesConfig
    app: AppConfig
    tz_view = tz.gettz('Europe/Moscow')
    tz_db = tz.gettz("UTC")

    @property
    def app_dir(self) -> Path:
        return self.paths.app_dir

    @property
    def config_path(self) -> Path:
        return self.paths.config_path

    @property
    def log_path(self) -> Path:
        return self.paths.log_path

    @property
    def temp_path(self) -> Path:
        return self.paths.temp_path


@dataclass
class Paths:
    app_dir: Path
    bot_name: str

    @property
    def config_path(self) -> Path:
        return self.app_dir / "config" / self.bot_name

    @property
    def logging_config_file(self) -> Path:
        return self.config_path / "logging.yaml"

    @property
    def log_path(self) -> Path:
        return self.app_dir / "log" / self.bot_name

    @property
    def temp_path(self) -> Path:
        return self.app_dir / "temp" / self.bot_name


@dataclass
class BotConfig:
    token: str
    log_chat: int
    superusers: list[int]
    enable_logging_middleware: bool
