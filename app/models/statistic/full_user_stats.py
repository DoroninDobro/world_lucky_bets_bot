from dataclasses import dataclass

from .transaction import TransactionStatData
from .user_stats import UserBetsStat
from app.models.db import User


@dataclass
class FullUserStat:
    bets: list[UserBetsStat]
    transactions: list[TransactionStatData]

    def get_user(self) -> User | None:
        try:
            return self.bets[0].user
        except IndexError:
            pass
        try:
            return self.transactions[0].user
        except IndexError:
            return None
