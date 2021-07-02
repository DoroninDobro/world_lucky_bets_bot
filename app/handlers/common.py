from aiogram import types
from tortoise.exceptions import DoesNotExist

from app.misc import dp
from app.models import User
from app.services.bets_log import remove_bet_item
from app.utils.exceptions import UserPermissionError


@dp.message_handler(commands="del", commands_prefix="/!")
async def remove_bet_item_command(message: types.Message, user: User):
    try:
        _, args = message.text.split(maxsplit=1)
        bet_item_id = int(args)
    except ValueError:
        return await message.reply(
            "After this command, be sure to specify the integer id bet, "
            "you want to delete"
        )
    try:
        bet_item = await remove_bet_item(bet_item_id, user)
    except UserPermissionError:
        return await message.reply("Not have permission to remove")
    except DoesNotExist:
        return await message.reply("No such entry was found")
    await message.reply(f"Deleted: {await bet_item.get_full_printable()}")
