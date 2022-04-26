# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger

from app.middlewares.db_middleware import DbMiddleware
from app import config


def setup(dispatcher: Dispatcher):
    logger.info("Configure middlewares...")
    dispatcher.middleware.setup(DbMiddleware())
    if config.ENABLE_LOGGING_MIDDLEWARE:
        logging_middleware = LoggingMiddleware()
        logging_middleware.logger = logger
        dispatcher.middleware.setup(logging_middleware)
