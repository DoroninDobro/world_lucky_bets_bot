# partially from https://github.com/aiogram/bot
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram_dialog import DialogRegistry
from loguru import logger

from app.config import load_config
from app.dialogs.panel import setup_dialogs
from app.models.config import Config
from app.models.config.main import Paths

paths = Paths(Path(__file__).parent.parent, os.getenv("BOT_NAME"))
config = load_config(paths)

bot = Bot(
    config.bot.token,
    parse_mode=types.ParseMode.HTML,
    disable_web_page_preview=True,
    protect_content=True,
)
dp = Dispatcher(bot, storage=config.storage.create_storage())
registry = DialogRegistry(dp)


def setup(current_config: Config):
    from app import filters
    from app import middlewares
    from app.utils import executor
    logger.debug(f"As application dir using: {current_config.app_dir}")

    middlewares.setup(dp, config=current_config)
    filters.setup(dp)
    executor.setup(current_config)

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers
    setup_dialogs(registry)
    # noinspection PyUnresolvedReferences
    from app.handlers import last
