from functools import partial

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from tortoise import Tortoise, run_async

from app.config import DBConfig

DECIMAL_CONFIG = dict(max_digits=12, decimal_places=4)


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


async def generate_schemas_db(db_config: DBConfig):
    await db_init(db_config)
    await Tortoise.generate_schemas()


def generate_schemas(db_config: DBConfig):
    run_async(generate_schemas_db(db_config))
