from dataclasses import dataclass
from decimal import Decimal

from app.models.config.currency import Currency, CurrenciesConfig
from app.models.db import BalanceEvent
from app.models.enum.blance_event_type import BalanceEventType


@dataclass
class TransactionData:
    user_id: int
    author_id: int
    currency: Currency
    amount: Decimal
    bet_log_item_id: int | None
    balance_event_type: BalanceEventType
    comment: str

    def print_(self):
        if self.is_by_admin:
            result = (
                f"📌 admin {self.author_id} add transaction for user {self.user_id}\n"
            )
        else:
            result = f"User {self.user_id} add transaction\n"
        result += (
            f"{self.amount:+.2f} {self.currency.symbol} "
            f"{self.comment}"
        )
        return result

    @property
    def is_by_admin(self):
        return self.user_id != self.author_id

    @property
    def is_income(self):
        return self.amount > 0

    @classmethod
    def from_db(cls, db: BalanceEvent, config: CurrenciesConfig):
        return cls(
            user_id=db.get_user_id(),
            author_id=db.get_author_id(),
            currency=config.currencies[db.currency],
            amount=db.delta,
            bet_log_item_id=db.get_bet_item_id(),
            balance_event_type=db.type_,
            comment=db.comment,
        )
