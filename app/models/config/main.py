from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from app.models.config.app_config import AppConfig
from app.models.config.currency import CurrenciesConfig
from app.models.config.db import DBConfig


@dataclass
class Config:
    paths: Paths
    db: DBConfig
    bot: BotConfig
    currencies: CurrenciesConfig
    app: AppConfig

    @property
    def app_dir(self) -> Path:
        return self.paths.app_dir

    @property
    def config_path(self) -> Path:
        return self.paths.config_path

    @property
    def log_path(self) -> Path:
        return self.paths.log_path


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


@dataclass
class BotConfig:
    token: str
    log_chat: int
    superusers: list[int]
