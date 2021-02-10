from time import time

from aiogram.types import InputFile

from app import config
from app.models import DataRange
from app.services.excel_writter import ExcelWriter
from app.services.reports.thread_users import generate_thread_users
from app.services.reports.total_report import generate_total_report
from app.services.reports.user_stat import generate_user_report


async def process_report(date_range: DataRange) -> InputFile:
    excel_writer = ExcelWriter()
    excel_writer.insert_total_report(await generate_total_report(date_range))
    excel_writer.insert_thread_users(await generate_thread_users(date_range))
    excel_writer.insert_users_reports(await generate_user_report(date_range))
    filename = config.app_dir / "temp" / f"rez{date_range}___{time()}.xlsx"
    excel_writer.save(filename)
    return InputFile(filename, f"{date_range}.xlsx")
