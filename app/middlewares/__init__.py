# partially from https://github.com/aiogram/bot
from aiogram import Dispatcher
from loguru import logger

from app.middlewares.acl import ACLMiddleware
from app.middlewares.access_control import AccessControlMiddleware
from app.config import allow_list


def setup(dispatcher: Dispatcher):
    logger.info("Configure middlewares...")
    dispatcher.middleware.setup(ACLMiddleware())
    dispatcher.middleware.setup(AccessControlMiddleware(allow_list))
