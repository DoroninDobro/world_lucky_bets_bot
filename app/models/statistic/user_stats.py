import typing
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app import config
from app.config.currency import Currency
from app.models.db import Bookmaker, User, WorkThread, BetItem


@dataclass
class UserStat:
    user: User

    day_name: typing.ClassVar = "Дата"
    day: date
    thread_id_name: typing.ClassVar = "Номер матча"
    thread_name_name: typing.ClassVar = "Название матча"
    thread: WorkThread
    total_bet_name: typing.ClassVar = f"Ставка"
    total_bet: Decimal
    total_payment_name: typing.ClassVar = f"Расчёт"
    total_payment: Decimal
    total_result_name: typing.ClassVar = f"Профит"
    total_result: Decimal
    currency: Currency
    total_bet_eur_name: typing.ClassVar = f"Ставка в в {config.BASE_CURRENCY}"
    total_bet_eur: Decimal
    total_payment_eur_name: typing.ClassVar = f"Расчёт в {config.BASE_CURRENCY}"
    total_payment_eur: Decimal
    total_result_eur_name: typing.ClassVar = f"Профит в {config.BASE_CURRENCY}"
    total_result_eur: Decimal
    bookmaker_name: typing.ClassVar = "Букмекер"
    bookmaker: Bookmaker

    bet_id_name: typing.ClassVar = "ID записи"
    bet_item: BetItem

    def get_captions(self):
        return [
            self.day_name,
            self.thread_id_name,
            self.thread_name_name,
            self.total_bet_name,
            self.total_payment_name,
            self.total_result_name,
            self.total_bet_eur_name,
            self.total_payment_eur_name,
            self.total_result_eur_name,
            self.bookmaker_name,
            self.bet_id_name,
        ]

    def get_printable(self):
        return [
            self.day,
            self.thread.id,
            self.thread.name,
            self.total_bet,
            self.total_payment,
            self.total_result,
            self.total_bet_eur,
            self.total_payment_eur,
            self.total_result_eur,
            self.bookmaker.name if self.bookmaker else "",
            self.bet_item.id,
        ]
