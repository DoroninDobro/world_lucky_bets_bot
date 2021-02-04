from datetime import datetime, date
from decimal import Decimal

from openexchangerates.client import OpenExchangeRatesClient

from app.services.rates.rates import Rates


class OpenExchangeRates(Rates):

    def __init__(self, api_key: str):
        super(OpenExchangeRates, self).__init__()
        self.api_key = api_key
        self.r = OpenExchangeRatesClient(api_key=self.api_key)

    async def get_updated_date(self) -> datetime:
        latest_res = await self.r.latest()
        return datetime.fromtimestamp(latest_res['timestamp'])

    async def _convert(self, code_from: str, code_to: str, value: Decimal = Decimal(1)) -> Decimal:
        if code_from == code_to:
            return value
        else:
            return value * await self.get_rate(code_from, code_to)

    async def get_rate(self, code_to: str, code_from: str) -> Decimal:
        if code_from == code_to:
            return Decimal(1)
        else:
            rates = (await self.r.latest())['rates']
            return rates[code_to] / rates[code_from]

    async def convert(
            self, code_from: str, code_to: str, value: Decimal = Decimal(1), day: date = None
    ) -> Decimal:
        if day is None:
            return await self._convert(code_from, code_to, value)
        if code_from == code_to:
            return value
        else:
            return value * await self.get_rate_historical(code_from, code_to, day)

    async def get_rate_historical(self, code_to: str, code_from: str, day: date) -> Decimal:
        if code_from == code_to:
            return Decimal(1)
        else:
            rates = (await self.r.historical(day))['rates']
            return rates[code_to] / rates[code_from]

    @property
    def source_rates(self):
        return 'OpenExchangeRates'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.r.close()
