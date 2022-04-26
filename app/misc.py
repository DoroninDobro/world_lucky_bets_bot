# partially from https://github.com/aiogram/bot
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry
from loguru import logger

from app import config
from app.dialogs.panel import setup_dialogs
from app.models.config.main import Paths

bot = Bot(
    config.BOT_TOKEN,
    parse_mode=types.ParseMode.HTML,
    disable_web_page_preview=True,
    protect_content=True,
)
dp = Dispatcher(bot, storage=MemoryStorage())
registry = DialogRegistry(dp)


def setup():
    from app import filters
    from app import middlewares
    from app.utils import executor
    logger.debug(f"As application dir using: {config.app_dir}")

    middlewares.setup(dp)
    filters.setup(dp)
    executor.setup(config.db_config)

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers
    setup_dialogs(registry)
    # noinspection PyUnresolvedReferences
    from app.handlers import last
