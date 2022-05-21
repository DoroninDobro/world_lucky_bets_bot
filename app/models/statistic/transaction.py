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

    date_columns = (1, )
    currency_columns = (4, )
    currency_eur_columns = (5, )
    all_currency_columns = (*currency_columns, *currency_eur_columns)
    names_columns = (8, )

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

    @classmethod
    def get_currencies_columns(cls, symbol: str, eur_symbol: str) -> dict[str, Iterable[int]]:
        if symbol == eur_symbol:
            return {
                symbol: cls.all_currency_columns,
            }
        return {
            symbol: cls.currency_columns,
            eur_symbol: cls.currency_eur_columns,
        }
