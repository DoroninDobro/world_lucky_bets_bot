# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger

from app.middlewares.db_middleware import DbMiddleware
from app.models.config import Config


def setup(dispatcher: Dispatcher, config: Config):
    logger.info("Configure middlewares...")
    dispatcher.middleware.setup(DbMiddleware(config))
    if config.bot.enable_logging_middleware:
        logging_middleware = LoggingMiddleware()
        logging_middleware.logger = logger
        dispatcher.middleware.setup(logging_middleware)
