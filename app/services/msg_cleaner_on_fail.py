import asyncio
import typing
from contextlib import asynccontextmanager

from aiogram import types

from app.services.remove_message import delete_message


@asynccontextmanager
async def msg_cleaner():
    """
    On enter return a list. Add aiogram.types.Message objects to the list,
    and all that messages will be removed on exit in case exceptions.
    """
    msgs: typing.List[types.Message] = []
    try:
        yield msgs
    except BaseException:
        await asyncio.gather(*[delete_message(msg) for msg in msgs])
        raise
