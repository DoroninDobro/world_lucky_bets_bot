import typing
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app import config


@dataclass
class TotalStatistic:
    day_name: typing.ClassVar = "Дата"
    day: date
    id_name: typing.ClassVar = "Номер матча"
    id: int
    total_bet_eur_name: typing.ClassVar = f"Общая сумма ставки в {config.BASE_CURRENCY}"
    total_bet_eur: Decimal
    total_payment_eur_name: typing.ClassVar = f"Общая сумма рассчёта в {config.BASE_CURRENCY}"
    total_payment_eur: Decimal
    total_result_eur_name: typing.ClassVar = f"Общий плюс в {config.BASE_CURRENCY}"
    total_result_eur: Decimal

    @classmethod
    def get_captions(cls) -> list[str]:
        return [
            cls.day_name,
            cls.id_name,
            cls.total_bet_eur_name,
            cls.total_payment_eur_name,
            cls.total_result_eur_name,
        ]

    def get_printable(self):
        return [
            self.day.isoformat(),
            self.id,
            self.total_bet_eur,
            self.total_payment_eur,
            self.total_result_eur,
        ]
