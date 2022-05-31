from tortoise import fields
from tortoise.models import Model

from .user import User
from .common import DECIMAL_CONFIG

from .bets_log import BetItem
from app.models.enum.blance_event_type import BalanceEventType
from ..config.currency import CurrenciesConfig


class BalanceEvent(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="balance_events",
    )
    author: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="balance_events_author",
    )
    at = fields.DatetimeField(auto_now=True, null=False)
    delta = fields.DecimalField(**DECIMAL_CONFIG)
    currency = fields.CharField(max_length=16)
    type_ = fields.CharEnumField(BalanceEventType, source_field="type")
    bet_item: fields.ForeignKeyRelation[BetItem] = fields.ForeignKeyField(
        "models.BetItem", related_name="balance_events",
    )
    comment = fields.TextField(null=True)

    class Meta:
        table = "balance_events"

    def __repr__(self):
        return (
            f"<BalanceEvent "
            f"id={self.id} "
            f">"
        )

    async def format_log(self):
        result = ""
        await self.fetch_related("author", "user")
        if self.is_by_admin:
            result += (
                f"📌 admin {self.author.mention_link} "
                f"add transaction of type {self.type_.value} "
                f"for user {self.user.mention_link} "
            )
        else:
            result += (
                f"{self.user.mention_link} "
                f"add transaction of type {self.type_.value} "
            )
        result += (
            f"{self.delta:+.2f} {self.currency} "
            f"{self.comment} "
        )
        return result

    async def format_history(self, currencies: CurrenciesConfig):
        await self.fetch_related("author", "user")
        result = f"{self.at.strftime('%d.%m.%Y')} "
        if self.is_by_admin:
            result += f"📌"
        else:
            result += ""
        result += (
            f"{self.delta:+.0f} {currencies.currencies[self.currency].symbol} "
            f"type: {self.type_.name} "
            f"{self.comment}"
        )
        return result

    def format_user(self, currencies: CurrenciesConfig):
        if self.type_ == BalanceEventType.SALARY:
            return (
                f"Your salary for that bet is "
                f"{-self.delta:+.0f} {currencies.currencies[self.currency].symbol} "
            )
        else:
            return (
                f"{self.delta:+.0f} {currencies.currencies[self.currency].symbol} "
                f"type: {self.type_.name} "
                f"{self.comment}"
            )

    @property
    def is_by_admin(self):
        return self.get_user_id() != self.get_author_id()

    # noinspection PyUnresolvedReferences
    def get_user_id(self):
        return self.user_id

    # noinspection PyUnresolvedReferences
    def get_author_id(self):
        return self.author_id

    # noinspection PyUnresolvedReferences
    def get_bet_item_id(self):
        return self.bet_item_id
