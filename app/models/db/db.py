from functools import partial

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from tortoise import Tortoise

from app.config import DBConfig


async def on_startup(_: Dispatcher, db_config: DBConfig):
    await db_init(db_config)


async def db_init(db_config: DBConfig):
    await Tortoise.init(
        db_url=db_config.create_url_config(),
        modules={'models': ['app.models']}
    )


async def on_shutdown(_: Dispatcher):
    await Tortoise.close_connections()


def setup(executor: Executor, db_config: DBConfig):
    executor.on_startup(partial(on_startup, db_config=db_config))
    executor.on_shutdown(on_shutdown)
