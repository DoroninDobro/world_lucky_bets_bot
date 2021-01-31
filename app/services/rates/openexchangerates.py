from datetime import datetime

from openexchangerates.client import OpenExchangeRatesClient

from app.services.rates.rates import Rates


class OpenExchangeRates(Rates):

    def __init__(self, api_key: str):
        super(OpenExchangeRates, self).__init__()
        self.api_key = api_key
        self.r = OpenExchangeRatesClient(api_key=self.api_key)

    async def get_updated_date(self):
        latest_res = await self.r.latest()
        return datetime.fromtimestamp(latest_res['timestamp']).isoformat()

    async def get_rate(self, char_val: str):
        if char_val == 'EUR':
            return 1
        else:
            rates = await self.r.latest()
            return rates['EUR'] / rates[char_val]

    def get_source_rates(self):
        return 'OpenExchangeRates'
