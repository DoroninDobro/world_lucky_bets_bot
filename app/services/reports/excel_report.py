from time import time

from aiogram.types import InputFile

from app.models import DataTimeRange
from app.models.config import Config
from app.services.excel_writter import ExcelWriter
from app.services.reports.thread_users import generate_thread_users
from app.services.reports.total_report import generate_total_report
from app.services.reports.user_stat import generate_user_report


async def process_report(date_range: DataTimeRange, config: Config) -> InputFile:
    excel_writer = ExcelWriter(config.currencies)
    excel_writer.insert_total_report(await generate_total_report(date_range, config.currencies))
    excel_writer.insert_thread_users(await generate_thread_users(date_range))
    excel_writer.insert_users_reports(await generate_user_report(date_range, config.currencies))
    filename = config.temp_path / f"rez{date_range}___{time()}.xlsx"
    excel_writer.save(filename)
    return InputFile(filename, f"{date_range}.xlsx")
