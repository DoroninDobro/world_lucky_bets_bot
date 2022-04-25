from decimal import Decimal

from app.models import User


async def calculate_balance(user: User) -> Decimal:
    """ TODO convert rates!! """
    return sum(map(lambda e: e.delta, await user.balance_events.all()))
