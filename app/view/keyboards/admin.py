import typing
from functools import lru_cache

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.models import AdditionalText, SendWorkers
from app.view.common import boolean_emoji

cb_stop = CallbackData("stop_thread", "thread_id")
cb_rename_thread = CallbackData("rename_thread", "thread_id")
cb_send_now = CallbackData("send_info", "additional_text")
cb_workers = CallbackData("send_info", "additional_text", "send_worker_id", "enable")
cb_update = CallbackData("update", "additional_text")
cb_is_disinformation = CallbackData("send_info", "additional_text", "is_disinformation")

all_time_report = "Отчёт за всё время"
last_month_report = "Отчёт за прошлый месяц"
current_moth_report = "Отчёт за этот месяц"


def get_work_thread_admin_kb(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton(
        "Stop", callback_data=cb_stop.new(thread_id=thread_id),
    ))
    _append_rename_button_to_kb(kb, thread_id)
    return kb


def get_stopped_work_thread_admin_kb(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    _append_rename_button_to_kb(kb, thread_id)
    return kb


def _append_rename_button_to_kb(kb: InlineKeyboardMarkup, thread_id: int):
    kb.insert(InlineKeyboardButton("Rename", callback_data=cb_rename_thread.new(thread_id=thread_id)))


def get_kb_menu_send(
        workers: typing.List[SendWorkers],
        additional_text: AdditionalText,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.insert(InlineKeyboardButton(
        "📬Send!",
        callback_data=cb_send_now.new(additional_text=additional_text.id),
    ))
    kb.insert(InlineKeyboardButton(
        "🔄Refresh",
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
        return boolean_emoji[not now_marked_as_disinformation] + "Turn off private mode"
    return boolean_emoji[not now_marked_as_disinformation] + "Turn on private mode"


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
