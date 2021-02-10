import typing
from functools import lru_cache
from typing import Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.config.currency import Currency
from app.models import AdditionalText, SendWorkers, User, WorkThread

cb_stop = CallbackData("stop_thread", "thread_id")
cb_agree = CallbackData("agree_thread", "thread_id")
cb_send_now = CallbackData("send_info", "additional_text")
cb_workers = CallbackData("send_info", "additional_text", "send_worker_id", "enable")
cb_update = CallbackData("update", "additional_text")
cb_is_disinformation = CallbackData("send_info", "additional_text", "is_disinformation")
cb_send_report = CallbackData("send_report", "user_id", "thread_id")
cb_currency = CallbackData("currency", "code")
cb_confirm_report = CallbackData("confirm", "yes")
cb_confirm_add_bookmaker = CallbackData("confirm_bookmaker", "yes")
boolean_emoji = {True: "✅", False: "🚫"}
all_time_report = "Отчёт за всё время"
last_month_report = "Отчёт за прошлый месяц"
current_moth_report = "Отчёт за этот месяц"


def get_stop_kb(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton("Остановить", callback_data=cb_stop.new(thread_id=thread_id)))
    return kb


def get_agree_work(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton("Буду работать +", callback_data=cb_agree.new(thread_id=thread_id)))
    return kb


def get_kb_menu_send(
        workers: typing.List[SendWorkers],
        additional_text: AdditionalText,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.insert(InlineKeyboardButton(
        "📬Отправить!",
        callback_data=cb_send_now.new(additional_text=additional_text.id),
    ))
    kb.insert(InlineKeyboardButton(
        "🔄Обновить",
        callback_data=cb_update.new(additional_text=additional_text.id),
    ))
    kb.insert(InlineKeyboardButton(
        get_disinformation_button_name(additional_text.is_disinformation),
        callback_data=cb_is_disinformation.new(
            additional_text=additional_text.id,
            is_disinformation=int(not additional_text.is_disinformation),
        )
    ))
    for worker in workers:
        kb.insert(InlineKeyboardButton(
            boolean_emoji[worker.send] + worker.worker.fullname,
            callback_data=cb_workers.new(
                additional_text=additional_text.id, send_worker_id=worker.id, enable=int(not worker.send)
            ),
        ))
    return kb


def get_disinformation_button_name(now_marked_as_disinformation: bool) -> str:
    if now_marked_as_disinformation:
        return boolean_emoji[not now_marked_as_disinformation] + "Выключить приватный режим"
    return boolean_emoji[not now_marked_as_disinformation] + "Включить приватный режим"


def get_kb_send_report(user: User, thread: WorkThread) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.insert(InlineKeyboardButton(
        "Отправить отчёт",
        callback_data=cb_send_report.new(user_id=user.id, thread_id=thread.id),
    ))
    return kb


def get_kb_currency(currencies: Dict[str, Currency]) -> InlineKeyboardMarkup:
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


@lru_cache
def get_reply_kb_report() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[
            KeyboardButton(all_time_report),
            KeyboardButton(last_month_report),
            KeyboardButton(current_moth_report),
        ]],
    )
