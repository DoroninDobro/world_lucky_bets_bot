from functools import lru_cache

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.models.config.currency import Currency

INCOME = "income"
EXPENSE = "outcome"
SIGNS = {INCOME: f"📈{INCOME}", EXPENSE: f"📉{EXPENSE}"}

cb_sign = CallbackData("transaction_sign", "sign")
cb_currency = CallbackData("transaction_currency", "code")
cb_complete = CallbackData("transaction_complete", "")


@lru_cache
def get_transaction_sign() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=[[
        InlineKeyboardButton(text, callback_data=cb_sign.new(sign=cb)) for cb, text in SIGNS.items()
    ]])


def get_kb_currency(currencies: dict[str, Currency]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=3)
    for currency in currencies.values():
        kb.insert(InlineKeyboardButton(
            str(currency),
            callback_data=cb_currency.new(code=currency.iso_code),
        ))
    return kb


@lru_cache
def get_kb_complete() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("complete", callback_data=cb_complete.new("*"))
    ]])
