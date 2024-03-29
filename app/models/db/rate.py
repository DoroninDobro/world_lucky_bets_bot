from decimal import Decimal

from tortoise import fields
from tortoise.models import Model

from app.utils.exceptions import CantConvertToThatCurrency

DECIMAL_CONFIG = dict(max_digits=12, decimal_places=4)
AVAILABLE_CURRENCIES_BASE = {"EUR", "USD"}


class RateItem(Model):
    id = fields.IntField(pk=True)
    at = fields.DateField(auto_now=True)
    currency = fields.CharField(max_length=16)
    to_eur = fields.DecimalField(**DECIMAL_CONFIG)
    to_usd = fields.DecimalField(**DECIMAL_CONFIG)

    class Meta:
        table = "historical_rates"
        unique_together = (("at", "currency"),)

    def convert_internal(self, code_to: str, value: Decimal) -> Decimal:
        return self.convert(self.currency, code_to, value)

    def convert(self, code_from: str, code_to: str, value: Decimal = Decimal(1)) -> Decimal:
        if code_from == code_to:
            return value
        else:
            return value * self.get_rate(code_from, code_to)

    def rate_internal(self, code_to: str) -> Decimal:
        return self.get_rate(self.currency, code_to)

    def get_rate(self, code_from: str, code_to: str) -> Decimal:
        available_currencies = AVAILABLE_CURRENCIES_BASE | {self.currency}
        if code_from not in available_currencies:
            raise CantConvertToThatCurrency(code_from)
        if code_to not in available_currencies:
            raise CantConvertToThatCurrency(code_to)

        to = {"USD": self.to_usd, "EUR": self.to_eur, self.currency: 1}
        return to[code_to] / to[code_from]

    def __repr__(self):
        return f"<RateItem id={self.id}>"
