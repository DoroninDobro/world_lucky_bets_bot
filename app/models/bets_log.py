from typing import NamedTuple

from tortoise import fields
from tortoise.models import Model

from .workers_in_threads import WorkerInThread


class BettingOdd(NamedTuple):
    money: int
    odd: float

    def __repr__(self):
        return f"{self.money} {self.odd}"


class BetItem(Model):
    id = fields.IntField(pk=True)
    created = fields.DatetimeField(auto_now=True)
    # noinspection PyUnresolvedReferences
    worker_thread: fields.ForeignKeyRelation[WorkerInThread] = fields.ForeignKeyField(
        'models.WorkerInThread', related_name='bets')
    money = fields.IntField()
    odd = fields.FloatField()

    class Meta:
        table = "bets_log"

    def __repr__(self):
        return f"<BetItem id={self.id}>"
