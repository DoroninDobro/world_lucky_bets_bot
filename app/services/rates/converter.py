from contextlib import suppress
from datetime import date
from decimal import Decimal

from tortoise.exceptions import IntegrityError

from app.models import DatetimeRange
from app.models.config.currency import CurrenciesConfig
from app.models.db import RateItem
from app.services.rates import OpenExchangeRates
from app.services.reports.common import get_month_rates


class RateConverter:

    def __init__(
            self,
            oer: OpenExchangeRates,
            rates: dict[date: list[RateItem]] = None,
            date_range: DatetimeRange = None,
            config: CurrenciesConfig = None,
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
        self.config = config

    async def init_rates(self):
        if self.rates is not None:
            return
        self.rates = await get_month_rates(self.date_range)

    async def find_rate_and_convert(
            self,
            value: Decimal,
            currency: str,
            day: date | None,
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
            if self.config:
                await save_daily_rates(self.config, self.oer)
            result = await self.oer.convert(currency, currency_to, value, day)
        else:
            result = rate.convert_internal(currency_to, value)
        return result


async def save_daily_rates(config: CurrenciesConfig, oer: OpenExchangeRates, using_db=None):
    with suppress(IntegrityError):
        for currency in config.currencies:
            rate = RateItem(
                at=(await oer.get_updated_date()).date(),
                currency=currency,
                to_eur=await oer.get_rate("EUR", currency),
                to_usd=await oer.get_rate("USD", currency),
            )
            await rate.save(using_db=using_db)
