from aiogram import types

from app.misc import dp
from app.models import DataRange
from app import keyboards as kb
from app.services.reports.excel_report import process_report


@dp.message_handler(text=kb.all_time_report, is_admin=True)
async def make_all_time_report(message: types.Message):
    try:
        date_range = DataRange.get_all_time_range()
        await message.reply_document(await process_report(date_range))
    except IndexError:
        await message.reply("Скорее всего за всё время ничего не было")


@dp.message_handler(text=kb.last_month_report, is_admin=True)
async def make_last_month_report(message: types.Message):
    try:
        date_range = DataRange.get_last_month_range()
        await message.reply_document(await process_report(date_range))
    except IndexError:
        await message.reply("Скорее всего в прошедшем месяце ничего не было")


@dp.message_handler(text=kb.current_moth_report, is_admin=True)
async def make_current_mont_report(message: types.Message):
    try:
        date_range = DataRange.get_current_month_range()
        await message.reply_document(await process_report(date_range))
    except IndexError:
        await message.reply("Скорее всего в этом месяце пока ничего не было")

