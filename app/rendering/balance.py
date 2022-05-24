from decimal import Decimal

from app.models import data
from app.models.config.currency import Currency
from app.models.enum.blance_event_type import BalanceEventType


def render_balance(balance: data.Balance, currency: Currency) -> str:
    result = ", ".join(map(
        lambda x: _render_money(x[1], x[0]),
        filter(lambda x: x[1] != 0, balance.amount.items()),
    ))
    result += f" (≈{_render_money(balance.amount_eur, currency)})"
    return result


def _render_money(amount: Decimal, currency: Currency) -> str:
    return f"{amount:.2f} {currency.symbol}"


def render_balance_type(balance_type: BalanceEventType) -> str:
    return balance_type.value
