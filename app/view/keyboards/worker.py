from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

cb_agree = CallbackData("agree_thread", "thread_id")


def get_agree_work(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton("I will work +", callback_data=cb_agree.new(thread_id=thread_id)))
    return kb
