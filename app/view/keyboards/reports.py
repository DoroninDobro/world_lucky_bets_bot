from functools import lru_cache

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.models.db import User, WorkThread
from app.models.config.currency import Currency
from app.view.common import boolean_emoji

cb_send_report = CallbackData("send_report", "user_id", "thread_id")
cb_currency = CallbackData("report_currency", "code")
cb_confirm_report = CallbackData("confirm", "yes")
cb_confirm_add_bookmaker = CallbackData("confirm_bookmaker", "yes")


def get_kb_send_report(user: User, thread: WorkThread) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.insert(InlineKeyboardButton(
        "Send report",
        callback_data=cb_send_report.new(user_id=user.id, thread_id=thread.id),
    ))
    return kb


def get_kb_currency(currencies: dict[str, Currency]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=3)
    for currency in currencies.values():
        kb.insert(InlineKeyboardButton(
            str(currency),
            callback_data=cb_currency.new(code=currency.iso_code),
        ))
    return kb


@lru_cache
def get_kb_confirm_report() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            boolean_emoji[yes],
            callback_data=cb_confirm_report.new(yes=str(yes))) for yes in (True, False)
    ]])


@lru_cache
def get_kb_confirm_add_bookmaker() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            boolean_emoji[yes],
            callback_data=cb_confirm_add_bookmaker.new(yes=str(yes))) for yes in (True, False)
    ]])
