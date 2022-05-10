from dataclasses import dataclass
from decimal import Decimal

from app.models.config.currency import Currency
from app.models.db import User
from app.models.enum.salary_type import SalaryType


@dataclass
class Bet:
    thread_id: int
    currency: Currency
    bet: Decimal
    result: Decimal
    bookmaker_id: str
    user: User

    @property
    def result_without_salary(self):
        return self.result - self.salary

    @property
    def profit_without_salary(self):
        return self.profit - self.salary

    @property
    def salary(self):
        match self.user.worker_status:
            case None:
                return 0
            case SalaryType.SALARY:
                return 0
            case SalaryType.BET_PERCENT:
                return self.user.calculate_piecework(self.bet)
            case SalaryType.WIN_PERCENT:
                if self.is_win:
                    return self.user.calculate_piecework(self.profit)
                else:
                    return 0
            case _:
                raise RuntimeError(f"unknown type of salary {self.user.worker_status}")

    @property
    def profit(self):
        return self.result - self.bet

    @property
    def is_win(self):
        return self.profit > 0
