import typing
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Union

from app.constants import BASE_CURRENCY
from app.models import WorkThread


@dataclass
class TotalStatistic:
    day_name: typing.ClassVar = "Дата"
    day: date
    thread_id_name: typing.ClassVar = "Номер матча"
    thread_name_name: typing.ClassVar = "Название матча"
    thread: WorkThread
    total_bet_eur_name: typing.ClassVar = f"Общая сумма ставки в {BASE_CURRENCY}"
    total_bet_eur: Decimal
    total_payment_eur_name: typing.ClassVar = f"Общая сумма расчёта в {BASE_CURRENCY}"
    total_payment_eur: Decimal
    total_result_eur_name: typing.ClassVar = f"Общий плюс в {BASE_CURRENCY}"
    total_result_eur: Decimal

    @classmethod
    def get_captions(cls) -> list[str]:
        return [
            cls.day_name,
            cls.thread_id_name,
            cls.thread_name_name,
            cls.total_bet_eur_name,
            cls.total_payment_eur_name,
            cls.total_result_eur_name,
        ]

    def get_printable(self) -> list[Union[str, date]]:
        return [
            self.day,
            self.thread.id,
            self.thread.name,
            self.total_bet_eur,
            self.total_payment_eur,
            self.total_result_eur,
        ]
