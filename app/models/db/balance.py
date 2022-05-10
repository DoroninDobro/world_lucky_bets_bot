from tortoise import fields
from tortoise.models import Model

from .user import User
from .common import DECIMAL_CONFIG

from .bets_log import BetItem
from app.models.enum.blance_event_type import BalanceEventType


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

    async def format(self, with_date: bool = True):
        result = ""
        await self.fetch_related("author", "user")
        if with_date:
            result += f"{self.at.strftime('%d.%B %H:%M')} "
        if self.is_by_admin:
            result += (
                f"📌 admin {self.author.mention_link} "
                f"add transaction for user {self.user.mention_link} "
            )
        else:
            result += f"{self.user.mention_link} add transaction "
        result += (
            f"{self.delta:.2f} {self.currency} "
            f"{self.comment}"
        )
        return result

    @property
    def is_by_admin(self):
        # noinspection PyUnresolvedReferences
        return self.user_id != self.author_id
