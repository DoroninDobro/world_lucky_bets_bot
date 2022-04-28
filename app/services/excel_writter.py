from dataclasses import dataclass
from typing import Iterable

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import numbers
from openpyxl.worksheet.worksheet import Worksheet

from app.config import BASE_CURRENCY
from app.models import TotalStatistic, UserStat
from app.models.config.currency import CurrenciesConfig
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

    def replace(self, *, row: int = None, column: int = None):
        return CellAddress(
            row=self.row if row is None else row,
            column=self.column if column is None else column
        )


A1 = CellAddress(1, 1)


class ExcelWriter:
    number_format = r"#,##0.00\ [$CURRENCY];[Red]-#,##0.00\ [$CURRENCY]"
    date_columns = (1, )
    name_columns = (3, )

    def __init__(self, config: CurrenciesConfig):
        self.wb = Workbook()
        self._remove_all_worksheets()
        self.current_currency = config.currencies[BASE_CURRENCY]

    def insert_total_report(self, report_data: dict[int, TotalStatistic]):
        total_ws = self.wb.create_sheet("Общая сводка матчей")
        _insert_row(total_ws, get_first_dict_value(report_data).get_captions(), A1)
        currencies_columns = {self.current_currency.symbol: (4, 5, 6)}

        for i, report_row in enumerate(sorted(report_data.values(), key=lambda ts: ts.thread.id), 1):
            _insert_row(total_ws, report_row.get_printable(), A1.shift(row=i))
            self.format_rows(total_ws, A1.shift(row=i), self.date_columns, currencies_columns)
        _make_auto_width(
            total_ws,
            len(get_first_dict_value(report_data).get_printable()),
            self.date_columns,
            currencies_columns,
            self.name_columns,
        )

    def insert_thread_users(self, report_data: list[ThreadUsers]):
        thread_users_ws = self.wb.create_sheet("Отчёты от работников")
        _insert_row(thread_users_ws, report_data[0].get_captions(), A1)
        for i, report_row in enumerate(report_data, 1):
            _insert_row(thread_users_ws, report_row.get_printable(), A1.shift(row=i))
            self.format_rows(thread_users_ws, A1.shift(row=i), self.date_columns, {})
        _make_auto_width(thread_users_ws, len(report_data[0].get_printable()), self.date_columns, {}, self.name_columns)

    def insert_users_reports(self, report_data: list[UserStat]):
        currencies_columns = {self.current_currency.symbol: (7, 8, 9)}
        local_currencies_columns = (4, 5, 6)
        bookmaker_name_col = 10
        names_cols = [bookmaker_name_col]
        column_count = len(report_data[0].get_printable())
        current_user = None
        current_user_ws = None  # it rewrite on first iteration, but linter don't think that
        i = 0  # it rewrite on first iteration, but linter don't think that
        for report_row in sorted(report_data, key=lambda x: x.user.id):
            if report_row.user != current_user:
                if current_user_ws is not None:
                    _make_auto_width(
                        current_user_ws,
                        column_count,
                        self.date_columns,
                        currencies=currencies_columns,
                        names=[*names_cols, *self.name_columns],
                    )
                current_user = report_row.user
                current_user_ws = self.wb.create_sheet(current_user.excel_caption_name)
                _insert_row(current_user_ws, report_row.get_captions(), A1)
                i = 1
            _insert_row(current_user_ws, report_row.get_printable(), A1.shift(row=i))
            self.format_rows(
                current_user_ws,
                A1.shift(row=i),
                self.date_columns,
                currencies=update_currency_dictionary(
                        currencies_columns, {report_row.currency.symbol: local_currencies_columns})
            )
            i += 1
        _make_auto_width(
            current_user_ws,
            column_count,
            self.date_columns,
            currencies=currencies_columns,
            names=[*names_cols, *self.name_columns],
        )

    def save(self, destination):
        self.wb.save(destination)

    def _remove_all_worksheets(self):
        for ws in self.wb.worksheets:
            self.wb.remove(ws)

    def format_rows(
            self,
            ws: Worksheet,
            first_cell: CellAddress,
            date_columns: Iterable[int],
            currencies: dict[str, Iterable[int]],
    ):
        for i in date_columns:
            cell = ws.cell(**first_cell.replace(column=i).kwargs)
            cell.number_format = numbers.FORMAT_DATE_DDMMYY  # noqa
        for currency, columns in currencies.items():
            for i in columns:
                cell = ws.cell(**first_cell.replace(column=i).kwargs)
                cell.number_format = self.number_format.replace("CURRENCY", currency)  # noqa


def _make_auto_width(
        total_ws: Worksheet,
        count: int,
        date_columns: Iterable[int],
        currencies: dict[str, Iterable[int]],
        names: Iterable[int] = tuple(),
):
    for i in range(1, count + 2):
        total_ws.column_dimensions[get_column_letter(i)].auto_size = True
    for i in date_columns:
        total_ws.column_dimensions[get_column_letter(i)].width += -3
    for i in names:
        total_ws.column_dimensions[get_column_letter(i)].width += 15
    if "Общая сводка матчей" in total_ws.title:
        width_add = 15
    else:
        width_add = 3
    for columns in currencies.values():
        for i in columns:
            total_ws.column_dimensions[get_column_letter(i)].width += width_add


def _insert_row(ws: Worksheet, data: list[str], first_cell: CellAddress):
    for i, text in enumerate(data):
        ws.cell(**first_cell.shift(column=i).kwargs, value=text)


def update_currency_dictionary(d1: dict[str, Iterable[int]], d2: dict[str, Iterable[int]]):
    result = dict(**d1)
    for key, value in d2.items():
        if key in result:
            result[key] = [*result[key], *d2[key]]
        else:
            result[key] = value
    return result
