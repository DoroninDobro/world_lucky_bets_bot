# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger

from app.middlewares.db_middleware import DbMiddleware
from app.models.config import Config
from app.services.rates import OpenExchangeRates


def setup(dispatcher: Dispatcher, config: Config):
    logger.info("Configure middlewares...")
    oer = OpenExchangeRates(api_key=config.currencies.oer_api_token)
    dispatcher.middleware.setup(DbMiddleware(config, oer=oer))
    if config.bot.enable_logging_middleware:
        logging_middleware = LoggingMiddleware()
        logging_middleware.logger = logger
        dispatcher.middleware.setup(logging_middleware)
