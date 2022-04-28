from contextlib import suppress

from aiogram import types
from aiogram.utils.exceptions import CantParseEntities, BotBlocked, BadRequest
from aiogram.utils.markdown import quote_html
from loguru import logger

from app.misc import config as global_config
from app.misc import dp, bot


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except CantParseEntities as e:
        logger.error("Cause exception {e} in update {update}", e=e, update=update)

    except BotBlocked:
        pass

    except Exception as e:
        logger.exception("Cause exception {e} in update {update}", e=e, update=update)

    user = get_user(update)
    if user.id in global_config.bot.superusers:
        # Vova don't wont receive errors with his actions in tech logs
        chat_id = user.id
    else:
        chat_id = global_config.app.chats.tech_log

    with suppress(BadRequest):
        await bot.send_message(
            chat_id,
            f"Exception {quote_html(exception)}\n"
            f"was received while processing an update {quote_html(update)}\n"
            f"{quote_html(exception.args)}"
        )
    return True


def get_user(update: types.Update) -> types.User:
    return update.message.from_user \
           or update.callback_query.from_user \
           or update.edited_message.from_user \
           or update.chosen_inline_result.from_user \
           or update.inline_query.from_user \
           or None
