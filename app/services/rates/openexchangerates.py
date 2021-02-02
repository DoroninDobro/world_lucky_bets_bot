from datetime import datetime

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

    async def get_rate(self, code_to: str, code_from: str):
        if code_from == code_to:
            return 1
        else:
            rates = await self.r.latest()
            return rates[code_to] / rates[code_from]

    def get_source_rates(self):
        return 'OpenExchangeRates'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.r.close()
