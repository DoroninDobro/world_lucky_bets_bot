from datetime import date
from decimal import Decimal

from app.models import RateItem
from app.services.rates import OpenExchangeRates
from app.config import BASE_CURRENCY


async def find_rate_and_convert(
        value: Decimal,
        currency: str,
        day: date,
        oer: OpenExchangeRates,
        rates: dict[date: list[RateItem]]
) -> Decimal:
    try:
        rate: RateItem = rates[day][currency]
    except KeyError:
        result = await oer.convert(currency, BASE_CURRENCY, value, day)
    else:
        result = rate.convert_internal(BASE_CURRENCY, value)
    return result
