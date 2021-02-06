import typing
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Union

from app import config
from app.models.db import User


@dataclass
class UserStat:
    user: User

    day_name: typing.ClassVar = "Дата"
    day: date
    id_name: typing.ClassVar = "Номер матча"
    id: int
    total_bet_name: typing.ClassVar = f"Ставка"
    total_bet: str
    total_payment_name: typing.ClassVar = f"Рассчёт"
    total_payment: str
    total_result_name: typing.ClassVar = f"Профит"
    total_result: str
    total_bet_eur_name: typing.ClassVar = f"Ставка в в {config.BASE_CURRENCY}"
    total_bet_eur: Decimal
    total_payment_eur_name: typing.ClassVar = f"Рассчёт в {config.BASE_CURRENCY}"
    total_payment_eur: Decimal
    total_result_eur_name: typing.ClassVar = f"Профит в {config.BASE_CURRENCY}"
    total_result_eur: Decimal

    def get_captions(self) -> list[str]:
        return [
            self.day_name,
            self.id_name,
            self.total_bet_name,
            self.total_payment_name,
            self.total_result_name,
            self.total_bet_eur_name,
            self.total_payment_eur_name,
            self.total_result_eur_name,
        ]

    def get_printable(self) -> list[Union[str, date]]:
        return [
            self.day,
            self.id,
            self.total_bet,
            self.total_payment,
            self.total_result,
            self.total_bet_eur,
            self.total_payment_eur,
            self.total_result_eur,
        ]
