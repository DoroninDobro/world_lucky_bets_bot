from decimal import Decimal

from app.models.data.bet import Bet
from app.models.data.transaction import TransactionData
from app.models.db import BetItem
from app.models.enum.blance_event_type import BalanceEventType


async def create_transactions_by_bet(bet_dto: Bet, bet: BetItem) -> list[TransactionData]:
    salary = bet_dto.salary
    amount = bet_dto.profit - salary
    transactions = [
        transaction_data_factory(
            bet=bet,
            amount=amount,
            type_=BalanceEventType.REPORT,
            bet_dao=bet_dto,
        ),
    ]
    if salary > 0:
        transactions.append(
            transaction_data_factory(
                bet=bet,
                amount=-salary,
                type_=BalanceEventType.SALARY,
                bet_dao=bet_dto,
            )
        )
    return transactions


def transaction_data_factory(
        bet: BetItem,
        amount: Decimal,
        type_: BalanceEventType,
        bet_dao: Bet,
        comment: str = "",
) -> TransactionData:
    return TransactionData(
        user_id=bet_dao.user.id,
        author_id=bet_dao.user.id,
        currency=bet_dao.currency,
        amount=amount,
        bet_log_item_id=bet.id,
        balance_event_type=type_,
        comment=comment,
    )
