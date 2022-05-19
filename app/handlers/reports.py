from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from loguru import logger

from app.misc import dp
from app.models import DataTimeRange
from app.view.keyboards import admin as kb
from app.models.config import Config
from app.services.reports.excel_report import process_report
from app.services.reports.thread_reports import get_thread_report


@dp.message_handler(text=kb.all_time_report, is_admin=True)
async def make_all_time_report(message: types.Message, config: Config):
    try:
        date_range = DataTimeRange.get_all_time_range()
        await generate_and_send_report(date_range, message, config)
    except IndexError:
        await message.reply(
            "Скорее всего за всё время ничего не было", protect_content=False,
        )


@dp.message_handler(text=kb.last_month_report, is_admin=True)
async def make_last_month_report(message: types.Message, config: Config):
    try:
        date_range = DataTimeRange.get_last_month_range()
        await generate_and_send_report(date_range, message, config)
    except IndexError:
        await message.reply(
            "Скорее всего в прошедшем месяце ничего не было", protect_content=False,
        )


@dp.message_handler(text=kb.current_week_report, is_admin=True)
async def make_current_mont_report(message: types.Message, config: Config):
    try:
        date_range = DataTimeRange.get_current_week_range()
        await generate_and_send_report(date_range, message, config)
    except IndexError:
        await message.reply(
            "Скорее всего на этой неделе пока ничего не было", protect_content=False,
        )


@dp.message_handler(text=kb.current_moth_report, is_admin=True)
async def make_current_mont_report(message: types.Message, config: Config):
    try:
        date_range = DataTimeRange.get_current_month_range()
        await generate_and_send_report(date_range, message, config)
    except IndexError:
        await message.reply(
            "Скорее всего в этом месяце пока ничего не было", protect_content=False,
        )


@dp.message_handler(commands="lumos")
async def match_report(m: types.Message, config: Config):
    try:
        _, args = m.text.split(maxsplit=1)
        thread_id = int(args)
        logger.info("user {user} ask report for {thread}", user=m.from_user.id, thread=thread_id)
    except ValueError as e:
        logger.info("user {user} ask report for thread but {e}", user=m.from_user.id, e=e)
        raise SkipHandler
    await m.reply(await get_thread_report(thread_id, config))


async def generate_and_send_report(date_range: DataTimeRange, message: types.Message, config: Config):
    await message.reply_document(
        await process_report(date_range, config),
        protect_content=False,
    )
