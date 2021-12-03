from functools import partial

from tortoise import Tortoise


async def on_startup(_, db_config):
    await db_init(db_config)


async def db_init(db_config):
    await Tortoise.init(
        db_url=db_config.create_url_config(),
        modules={'models': ['app.models']}
    )


async def on_shutdown(_):
    await Tortoise.close_connections()


def setup(executor, db_config):
    executor.on_startup(partial(on_startup, db_config=db_config))
    executor.on_shutdown(on_shutdown)
