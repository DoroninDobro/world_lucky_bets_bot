import typing

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.models import AdditionalText, SendWorkers

cb_stop = CallbackData("stop_thread", "thread_id")
cb_agree = CallbackData("agree_thread", "thread_id")
cb_send_now = CallbackData("send_info", "additional_text")
cb_workers = CallbackData("send_info", "additional_text", "send_worker_id", "enable")
cb_is_disinformation = CallbackData("send_info", "additional_text", "is_disinformation")
permissions_emoji = {True: "✅", False: "🚫"}


def get_stop_kb(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton("Остановить", callback_data=cb_stop.new(thread_id=thread_id)))
    return kb


def get_agree_work(thread_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton("Буду работать", callback_data=cb_agree.new(thread_id=thread_id)))
    return kb


def get_kb_menu_send(
        workers: typing.List[SendWorkers],
        additional_text: AdditionalText,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.insert(InlineKeyboardButton(
        "Отправить!",
        callback_data=cb_send_now.new(additional_text=additional_text.id)
    ))
    kb.insert(InlineKeyboardButton(
        "Пометить как дезу" if not additional_text.is_disinformation else "Пометить как правдивую",
        callback_data=cb_is_disinformation.new(
            additional_text=additional_text.id,
            is_disinformation=int(not additional_text.is_disinformation)
        )
    ))
    for worker in workers:
        kb.insert(InlineKeyboardButton(
            permissions_emoji[worker.send] + worker.worker.fullname,
            callback_data=cb_workers.new(
                additional_text=additional_text.id, send_worker_id=worker.id, enable=int(not worker.send)
            )
        ))
    return kb
