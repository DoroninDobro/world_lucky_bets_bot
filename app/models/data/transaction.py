from dataclasses import dataclass
from decimal import Decimal

from app.models.config.currency import Currency


@dataclass
class TransactionData:
    user_id: int
    author_id: int
    is_income: bool
    currency: Currency
    amount: Decimal
    comment: str
