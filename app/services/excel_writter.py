from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.models import TotalStatistic


@dataclass
class CellAddress:
    row: int
    column: int

    @property
    def kwargs(self, ):
        return dict(row=self.row, column=self.column)

    def shift(self, *, row: int = 0, column: int = 0):
        return CellAddress(row=self.row + row, column=self.column + column)


class ExcelWriter:
    def __init__(self):
        self.wb = Workbook(iso_dates=True)
        self._remove_all_worksheets()

    def insert_total_report(self, report_data: dict[int, TotalStatistic]):
        a1 = CellAddress(1, 1)
        total_ws = self.wb.create_sheet("общая сводка  матчей")
        _insert_row(total_ws, TotalStatistic.get_captions(), a1)
        for i, report_row in enumerate(sorted(report_data.values(), key=lambda ts: ts.id), 1):
            _insert_row(total_ws, report_row.get_printable(), a1.shift(row=i))

    def save(self, path: Path):
        self.wb.save(path)

    def _remove_all_worksheets(self):
        for ws in self.wb.worksheets:
            self.wb.remove(ws)


def _insert_row(ws: Worksheet, data: list[str], first_cell: CellAddress):
    for i, text in enumerate(data):
        ws.cell(**first_cell.shift(column=i).kwargs, value=text)
