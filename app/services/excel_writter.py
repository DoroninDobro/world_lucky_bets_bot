from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.models import TotalStatistic, UserStat
from app.models.statistic.thread_users import ThreadUsers
from app.services.collections_utils import get_first_dict_value


@dataclass
class CellAddress:
    row: int
    column: int

    @property
    def kwargs(self, ):
        return dict(row=self.row, column=self.column)

    def shift(self, *, row: int = 0, column: int = 0):
        return CellAddress(row=self.row + row, column=self.column + column)


A1 = CellAddress(1, 1)


class ExcelWriter:
    def __init__(self):
        self.wb = Workbook()
        self._remove_all_worksheets()

    def insert_total_report(self, report_data: dict[int, TotalStatistic]):
        total_ws = self.wb.create_sheet("Общая сводка  матчей")
        _insert_row(total_ws, get_first_dict_value(report_data).get_captions(), A1)
        for i, report_row in enumerate(sorted(report_data.values(), key=lambda ts: ts.id), 1):
            _insert_row(total_ws, report_row.get_printable(), A1.shift(row=i))

    def insert_thread_users(self, report_data: list[ThreadUsers]):
        thread_users_ws = self.wb.create_sheet("Отчёты от работников")
        _insert_row(thread_users_ws, report_data[0].get_captions(), A1)
        for i, report_row in enumerate(report_data, 1):
            _insert_row(thread_users_ws, report_row.get_printable(), A1.shift(row=i))

    def insert_users_reports(self, report_data: list[UserStat]):
        current_user = None
        current_user_ws = None  # it rewrite on first iteration, but linter don't think that
        i = None  # it rewrite on first iteration, but linter don't think that
        for report_row in sorted(report_data, key=lambda x: x.user.id):
            if report_row.user != current_user:
                current_user = report_row.user
                current_user_ws = self.wb.create_sheet(current_user.fullname)
                _insert_row(current_user_ws, report_row.get_captions(), A1)
                i = 1
            _insert_row(current_user_ws, report_row.get_printable(), A1.shift(row=i))
            i += 1

    def save(self, destination):
        self.wb.save(destination)

    def _remove_all_worksheets(self):
        for ws in self.wb.worksheets:
            self.wb.remove(ws)


def _insert_row(ws: Worksheet, data: list[str], first_cell: CellAddress):
    for i, text in enumerate(data):
        ws.cell(**first_cell.shift(column=i).kwargs, value=text)
