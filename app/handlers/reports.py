from aiogram import types
from aiogram.dispatcher.handler import SkipHandler

from app.misc import dp
from app.models import DataTimeRange
from app import keyboards as kb
from app.services.reports.excel_report import process_report
from app.services.reports.thread_reports import get_thread_report


@dp.message_handler(text=kb.all_time_report, is_admin=True)
async def make_all_time_report(message: types.Message):
    try:
        date_range = DataTimeRange.get_all_time_range()
        await generate_and_send_report(date_range, message)
    except IndexError:
        await message.reply(
            "Скорее всего за всё время ничего не было", protect_content=False,
        )


@dp.message_handler(text=kb.last_month_report, is_admin=True)
async def make_last_month_report(message: types.Message):
    try:
        date_range = DataTimeRange.get_last_month_range()
        await generate_and_send_report(date_range, message)
    except IndexError:
        await message.reply(
            "Скорее всего в прошедшем месяце ничего не было", protect_content=False,
        )


@dp.message_handler(text=kb.current_moth_report, is_admin=True)
async def make_current_mont_report(message: types.Message):
    try:
        date_range = DataTimeRange.get_current_month_range()
        await generate_and_send_report(date_range, message)
    except IndexError:
        await message.reply(
            "Скорее всего в этом месяце пока ничего не было", protect_content=False,
        )


@dp.message_handler(commands="lumos")
async def match_report(m: types.Message):
    _, args = m.text.split(maxsplit=1)
    try:
        thread_id = int(args)
    except ValueError:
        raise SkipHandler
    await m.reply(await get_thread_report(thread_id))


async def generate_and_send_report(date_range: DataTimeRange, message: types.Message):
    await message.reply_document(
        await process_report(date_range),
        protect_content=False,
    )


