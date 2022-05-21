from dataclasses import dataclass

from .transaction import TransactionStatData
from .user_stats import UserBetsStat


@dataclass
class FullUserStat:
    bets: list[UserBetsStat]
    transactions: list[TransactionStatData]
