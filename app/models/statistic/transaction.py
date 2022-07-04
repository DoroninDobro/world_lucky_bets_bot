from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from app.models.config.currency import Currency
from app.models.db import User
from app.models.enum.blance_event_type import BalanceEventType
from app.constants import BASE_CURRENCY
from app.rendering.balance import render_balance_type


@dataclass
class TransactionStatData:
    id: int
    at: datetime
    user: User
    author_id: User
    currency: Currency
    amount: Decimal
    amount_eur: Decimal
    bet_log_item_id: int | None
    balance_event_type: BalanceEventType
    comment: str

    def get_printable(self) -> list[str | datetime | int]:
        return [
            self.at.replace(tzinfo=None),
            self.id,
            self.author_id if self.by_admin else "",
            self.amount,
            self.amount_eur,
            render_balance_type(self.balance_event_type),
            self.bet_log_item_id,
            self.comment,
        ]

    @property
    def by_admin(self) -> bool:
        return self.author_id != self.user.id


@dataclass
class TransactionStatCaptions:
    at: str = "Дата"
    id: str = "ID"
    by_admin: str = "От админа"
    amount: str = "Итого"
    amount_eur: str = f"Итого {BASE_CURRENCY}"
    type: str = "Тип"
    bet_log_id: str = "ID ставки"
    comment: str = "Комментарий"

    _date_columns = (1,)
    _currency_columns = (4,)
    _currency_eur_columns = (5,)
    _all_currency_columns = (*_currency_columns, *_currency_eur_columns)
    _names_columns = (8,)

    def __init__(self, first_col: int = 1):
        self.offset = first_col - 1

    @classmethod
    def get_captions(cls) -> list[str]:
        return [
            cls.at,
            cls.id,
            cls.by_admin,
            cls.amount,
            cls.amount_eur,
            cls.type,
            cls.bet_log_id,
            cls.comment,
        ]

    @classmethod
    def get_count_columns(cls):
        return len(cls.get_captions())

    def get_currencies_columns(self, symbol: str, eur_symbol: str) -> dict[str, Iterable[int]]:
        if symbol == eur_symbol:
            return {
                symbol: self._patch_column_iterable(self._all_currency_columns),
            }
        return {
            symbol: self._patch_column_iterable(self._currency_columns),
            eur_symbol: self._patch_column_iterable(self._currency_eur_columns),
        }

    def get_date_columns(self):
        return self._patch_column_iterable(self._date_columns)

    def get_currency_columns(self):
        return self._patch_column_iterable(self._currency_columns)

    def get_currency_eur_columns(self):
        return self._patch_column_iterable(self._currency_eur_columns)

    def get_all_currency_columns(self):
        return self._patch_column_iterable(self._all_currency_columns)

    def get_names_columns(self):
        return self._patch_column_iterable(self._names_columns)

    def _patch_column_iterable(self, columns: Iterable[int]) -> Iterable[int]:
        return map(self.patch_column_by_offset, columns)

    def patch_column_by_offset(self, col: int) -> int:
        return col + self.offset
