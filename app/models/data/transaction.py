from dataclasses import dataclass
from decimal import Decimal

from app.models.config.currency import Currency
from app.models.enum.blance_event_type import BalanceEventType


@dataclass
class TransactionData:
    user_id: int
    author_id: int
    is_income: bool
    currency: Currency
    amount: Decimal
    bet_log_item_id: int | None
    balance_event_type: BalanceEventType
    comment: str

    def __str__(self):
        if self.is_by_admin:
            result = (
                f"📌 admin {self.author_id} add transaction for user {self.user_id}\n"
            )
        else:
            result = f"User {self.user_id} add transaction\n"
        result += (
            f"{'income' if self.is_income else 'expense'} "
            f"{self.amount:.2f} {self.currency.symbol} "
            f"{self.comment}"
        )
        return result

    @property
    def is_by_admin(self):
        return self.user_id != self.author_id
