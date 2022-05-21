from datetime import date
from decimal import Decimal

from app.models import DataTimeRange
from app.models.db import RateItem
from app.services.rates import OpenExchangeRates
from app.services.reports.common import get_month_rates


class RateConverter:

    def __init__(
            self,
            oer: OpenExchangeRates,
            rates: dict[date: list[RateItem]] = None,
            date_range: DataTimeRange = None,
    ):
        """
        :param oer: - OpenExchangeRates - with that can search not founded rate
        :param rates: - collection contains rates on dates of needed range
        :date_range: - interval for loading rates from db
        """
        self.oer = oer
        if rates is None and date_range is None:
            raise RuntimeError("rates and date_range are both None!")
        self.rates = rates
        self.date_range = date_range

    async def init_rates(self):
        if self.rates is not None:
            return
        self.rates = await get_month_rates(self.date_range)

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
        await self.init_rates()
        try:
            rate: RateItem = self.rates[day][currency]
        except KeyError:
            result = await self.oer.convert(currency, currency_to, value, day)
        else:
            result = rate.convert_internal(currency_to, value)
        return result
