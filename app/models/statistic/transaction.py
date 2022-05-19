from dataclasses import dataclass
from decimal import Decimal

from app.models.config.currency import Currency
from app.models.db import User
from app.models.enum.blance_event_type import BalanceEventType


@dataclass
class TransactionStatData:
    user: User
    author_id: User
    currency: Currency
    amount: Decimal
    bet_log_item_id: int | None
    balance_event_type: BalanceEventType
    comment: str
