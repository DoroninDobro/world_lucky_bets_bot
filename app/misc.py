from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app import config

bot = Bot(config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


def setup():
    from app import filters
    from app import middlewares
    from app.utils import executor

    middlewares.setup(dp)
    filters.setup(dp)
    executor.setup(config.db_config)
    import app.handlers
