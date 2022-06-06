from aiogram import types
from tortoise.exceptions import DoesNotExist

from app.misc import dp
from app.models.db import User
from app.models.config import Config
from app.services.balance import remove_transaction
from app.services.bets_log import remove_bet_item
from app.utils.exceptions import UserPermissionError


@dp.message_handler(commands="del", commands_prefix="/!")
async def remove_bet_item_command(message: types.Message, user: User, config: Config):
    bet_item_id = await get_command_int_arg_or_notify(message)
    try:
        bet_item = await remove_bet_item(bet_item_id, user, config)
    except UserPermissionError:
        return await message.reply("Not have permission to remove")
    except DoesNotExist:
        return await message.reply("No such entry was found")
    await message.reply(f"Deleted: {await bet_item.get_full_printable()}")


@dp.message_handler(commands="del_transaction", commands_prefix="/!", is_admin=True)
async def remove_transaction_cmd(message: types.Message, user: User, config: Config):
    transaction_id = await get_command_int_arg_or_notify(message)
    try:
        transaction = await remove_transaction(transaction_id, user, config)
    except UserPermissionError as e:
        return await message.reply("Not have permission to remove\n" + e.text)
    except DoesNotExist:
        return await message.reply("No such entry was found")
    await message.reply(f"Deleted: {transaction.id}")


async def get_command_int_arg_or_notify(message: types.Message) -> int:
    try:
        _, args = message.text.split(maxsplit=1)
        return int(args)
    except ValueError:
        await message.reply(
            "After this command, be sure to specify the integer id bet, "
            "you want to delete"
        )
        raise
