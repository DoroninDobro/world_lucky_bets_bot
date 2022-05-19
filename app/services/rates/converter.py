from datetime import date
from decimal import Decimal

from app.models.db import RateItem
from app.services.rates import OpenExchangeRates


class RateConverter:

    def __init__(self, oer: OpenExchangeRates, rates: dict[date: list[RateItem]]):
        """
        :param oer: - OpenExchangeRates - with that can search not founded rate
        :param rates: - collection contains rates on dates of needed range
        """
        self.oer = oer
        self.rates = rates

    async def find_rate_and_convert(
            self,
            value: Decimal,
            currency: str,
            day: date,
            currency_to: str,
    ) -> Decimal:
        """
        :param value: - value of money that need convert
        :param currency: - ISO code for currency from
        :param day: - date for search rate convert
        :param currency_to: - ISO code for currency to
        """
        try:
            rate: RateItem = self.rates[day][currency]
        except KeyError:
            result = await self.oer.convert(currency, currency_to, value, day)
        else:
            result = rate.convert_internal(currency_to, value)
        return result
