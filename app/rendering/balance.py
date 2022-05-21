from decimal import Decimal

from app.models.config.currency import Currency
from app.models.enum.blance_event_type import BalanceEventType


def render_balance(balance: Decimal, currency: Currency):
    return f"{balance:.2f} {currency.symbol}"


def render_balance_type(balance_type: BalanceEventType) -> str:
    return balance_type.value
