from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Union

from app.constants import BASE_CURRENCY
from app.models.config.currency import Currency
from app.models.db import Bookmaker, User, WorkThread, BetItem


@dataclass
class UserBetsStat:
    user: User

    day: date
    thread: WorkThread
    total_bet: Decimal
    total_payment: Decimal
    total_result: Decimal
    currency: Currency
    total_bet_eur: Decimal
    total_payment_eur: Decimal
    total_result_eur: Decimal
    bookmaker: Bookmaker

    bet_item: BetItem

    def get_printable(self) -> list[Union[str, date]]:
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


class UserStatCaptions:
    """TODO make same like app.models.statistic.transaction.TransactionStatCaptions"""
    day_name = "Дата"
    thread_id_name = "Номер матча"
    thread_name_name = "Название матча"
    total_bet_name = f"Ставка"
    total_payment_name = f"Расчёт"
    total_result_name = f"Профит"
    total_bet_eur_name = f"Ставка в в {BASE_CURRENCY}"
    total_payment_eur_name = f"Расчёт в {BASE_CURRENCY}"
    total_result_eur_name = f"Профит в {BASE_CURRENCY}"
    bookmaker_name = "Букмекер"
    bet_id_name = "ID записи"

    @classmethod
    def get_captions(cls) -> list[str]:
        return [
            cls.day_name,
            cls.thread_id_name,
            cls.thread_name_name,
            cls.total_bet_name,
            cls.total_payment_name,
            cls.total_result_name,
            cls.total_bet_eur_name,
            cls.total_payment_eur_name,
            cls.total_result_eur_name,
            cls.bookmaker_name,
            cls.bet_id_name,
        ]
