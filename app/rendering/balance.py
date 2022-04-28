from decimal import Decimal

from app.models.config.currency import Currency


def render_balance(balance: Decimal, currency: Currency):
    return f"{balance:.2f} {currency.symbol}"
