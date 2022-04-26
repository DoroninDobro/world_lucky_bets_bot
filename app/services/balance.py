from decimal import Decimal

from app.models import User, BalanceEvent
from app.services.rates import OpenExchangeRates
from app.services.rates.utils import find_rate_and_convert
from app.services.reports.common import get_rates_by_date


async def calculate_balance(user: User, oer: OpenExchangeRates) -> Decimal:
    """ TODO convert rates!! """
    balance_sum = Decimal(0)
    for balance_event in await user.balance_events.all():
        balance_event: BalanceEvent
        balance_sum += await find_rate_and_convert(
            value=balance_event.delta,
            currency=balance_event.currency,
            day=balance_event.at,
            oer=oer,
            rates=await get_rates_by_date(balance_event.at)
        )
    return balance_sum
