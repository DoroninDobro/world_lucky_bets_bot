from datetime import date
from decimal import Decimal

from app.models import RateItem
from app.services.rates import OpenExchangeRates


async def find_rate_and_convert(
        value: Decimal,
        currency: str,
        day: date,
        oer: OpenExchangeRates,
        rates: dict[date: list[RateItem]],
        currency_to: str,
) -> Decimal:
    """
    :param value: - value of money that need convert
    :param currency: - ISO code for currency from
    :param day: - date for search rate convert
    :param oer: - OpenExchangeRates - with that can search not founded rate
    :param rates: - collection contains rates on dates of needed range
    :param currency_to: - ISO code for currency to
    """
    try:
        rate: RateItem = rates[day][currency]
    except KeyError:
        result = await oer.convert(currency, currency_to, value, day)
    else:
        result = rate.convert_internal(currency_to, value)
    return result
