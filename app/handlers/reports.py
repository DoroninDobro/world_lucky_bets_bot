from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from loguru import logger

from app.misc import dp
from app.models import DatetimeRange
from app.services.rates import OpenExchangeRates
from app.view.keyboards import admin as kb
from app.models.config import Config
from app.services.reports.excel_report import process_report
from app.services.reports.thread_reports import get_thread_report

KB_RANGES = {
    kb.all_time_report: DatetimeRange.get_all_time_range,
    kb.last_month_report: DatetimeRange.get_last_month_range,
    kb.current_week_report: DatetimeRange.get_current_week_range,
    kb.current_moth_report: DatetimeRange.get_current_month_range,
}


@dp.message_handler(text=KB_RANGES, is_admin=True)
async def make_all_time_report(message: types.Message, config: Config, oer: OpenExchangeRates):
    try:
        date_range = KB_RANGES[message.text]()
        await message.reply_document(
            await process_report(date_range, config, oer),
            protect_content=False,
        )
    except IndexError:
        await message.reply(
            "Скорее всего за данный промежуток ничего не было", protect_content=False,
        )


@dp.message_handler(commands="lumos")
async def match_report(m: types.Message, config: Config, oer: OpenExchangeRates):
    try:
        _, args = m.text.split(maxsplit=1)
        thread_id = int(args)
        logger.info("user {user} ask report for {thread}", user=m.from_user.id, thread=thread_id)
    except ValueError as e:
        logger.info("user {user} ask report for thread but {e}", user=m.from_user.id, e=e)
        raise SkipHandler
    await m.reply(await get_thread_report(thread_id, config, oer))
