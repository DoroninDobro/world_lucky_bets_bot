from tortoise import fields
from tortoise.models import Model

from .user import User
from .db import DECIMAL_CONFIG


class BalanceEvent(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="balance_events",
    )
    at = fields.DatetimeField(auto_now=True, null=False)
    delta = fields.DecimalField(**DECIMAL_CONFIG)
    currency = fields.CharField(max_length=16)
    comment = fields.TextField(null=True)

    class Meta:
        table = "balance_events"

    def __repr__(self):
        return (
            f"<BalanceEvent "
            f"id={self.id} "
            f">"
        )
