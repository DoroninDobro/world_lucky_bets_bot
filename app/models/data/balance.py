from dataclasses import dataclass
from decimal import Decimal

from app.models.config.currency import Currency


@dataclass
class Balance:
    amount: dict[Currency, Decimal]
    amount_eur: Decimal
