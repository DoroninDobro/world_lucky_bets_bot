from dataclasses import dataclass
from typing import Iterable

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import numbers
from openpyxl.worksheet.worksheet import Worksheet

from app.models import TotalStatistic, UserBetsStat
from app.models.config.currency import CurrenciesConfig
from app.models.statistic.full_user_stats import FullUserStat
from app.models.statistic.thread_users import ThreadUsers
from app.models.statistic.transaction import TransactionStatData
from app.models.statistic.user_stats import UserStatCaptions
from app.services.collections_utils import get_first_dict_value
from app.services.reports.common import excel_bets_caption_name, excel_transaction_caption_name


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
        self.current_currency = config.default_currency

        self.user_currencies_columns = {self.current_currency.symbol: (7, 8, 9)}
        self.user_local_currencies_columns = (4, 5, 6)
        self.user_bookmaker_name_col = 10
        self.user_names_cols = [self.user_bookmaker_name_col]

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

    def insert_users_reports(self, report_data: dict[int, FullUserStat]):
        # sorted by user_id for consistent sheets order
        # after sorting user_ids (dict key) don't need anymore
        sorted_reports: Iterable[FullUserStat] = map(lambda x: x[1], sorted(report_data.items(), key=lambda x: x[0]))

        for report_by_user in sorted_reports:
            self.write_user_bets_report(report_by_user.bets)
            self.write_user_transaction(report_by_user.transactions)

    def write_user_bets_report(self, report_by_user: list[UserBetsStat]):
        if not report_by_user:
            return
        column_count = len(UserStatCaptions.get_captions())
        sheet = self.wb.create_sheet(excel_bets_caption_name(report_by_user[0].user))
        _make_auto_width(
            sheet,
            column_count,
            self.date_columns,
            currencies=self.user_currencies_columns,
            names=[*self.user_names_cols, *self.name_columns],
        )
        _insert_row(sheet, UserStatCaptions.get_captions(), A1)
        for i, report_row in enumerate(report_by_user, 1):
            _insert_row(sheet, report_row.get_printable(), A1.shift(row=i))
            self.format_rows(
                sheet,
                A1.shift(row=i),
                self.date_columns,
                currencies=update_currency_dictionary(
                    self.user_currencies_columns, {report_row.currency.symbol: self.user_local_currencies_columns})
            )

    def write_user_transaction(self, transactions: list[TransactionStatData]):
        if not transactions:
            return
        sheet = self.wb.create_sheet(excel_transaction_caption_name(transactions[0].user))
        # TODO

    def save(self, destination):
        self.wb.save(destination)

    def _remove_all_worksheets(self):
        for ws in self.wb.worksheets:
            self.wb.remove(ws)

    def format_rows(
            self,
            sheet: Worksheet,
            first_cell: CellAddress,
            date_columns: Iterable[int],
            currencies: dict[str, Iterable[int]],
    ):
        for i in date_columns:
            cell = sheet.cell(**first_cell.replace(column=i).kwargs)
            cell.number_format = numbers.FORMAT_DATE_DDMMYY  # noqa
        for currency, columns in currencies.items():
            for i in columns:
                cell = sheet.cell(**first_cell.replace(column=i).kwargs)
                cell.number_format = self.number_format.replace("CURRENCY", currency)  # noqa


def _make_auto_width(
        sheet: Worksheet,
        count: int,
        date_columns: Iterable[int],
        currencies: dict[str, Iterable[int]],
        names: Iterable[int] = tuple(),
):
    for i in range(1, count + 2):
        sheet.column_dimensions[get_column_letter(i)].auto_size = True
    for i in date_columns:
        sheet.column_dimensions[get_column_letter(i)].width += -3
    for i in names:
        sheet.column_dimensions[get_column_letter(i)].width += 15
    if "Общая сводка матчей" in sheet.title:
        width_add = 15
    else:
        width_add = 3
    for columns in currencies.values():
        for i in columns:
            sheet.column_dimensions[get_column_letter(i)].width += width_add


def _insert_row(sheet: Worksheet, data: list[str], first_cell: CellAddress):
    for i, text in enumerate(data):
        sheet.cell(**first_cell.shift(column=i).kwargs, value=text)


def update_currency_dictionary(d1: dict[str, Iterable[int]], d2: dict[str, Iterable[int]]):
    result = dict(**d1)
    for key, value in d2.items():
        if key in result:
            result[key] = [*result[key], *d2[key]]
        else:
            result[key] = value
    return result
