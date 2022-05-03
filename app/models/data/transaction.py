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

    def __str__(self):
        if self.is_by_admin:
            result = (
                f"📌 by admin {self.author_id} for user {self.user_id}\n"
            )
        else:
            result = f"User {self.user_id} add transaction "
        result += (
            f"{'income' if self.is_income else 'expense'} "
            f"{self.amount:.2f} {self.currency.symbol} "
            f"{self.comment}"
        )
        return result

    @property
    def is_by_admin(self):
        return self.user_id != self.author_id
