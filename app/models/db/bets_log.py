from tortoise import fields
from tortoise.models import Model

from .db import DECIMAL_CONFIG
from .workers_in_threads import WorkerInThread
from .bookmaker import Bookmaker


class BetItem(Model):
    id = fields.IntField(pk=True)
    created = fields.DatetimeField(generated=True)
    # noinspection PyUnresolvedReferences
    worker_thread: fields.ForeignKeyRelation[WorkerInThread] = fields.ForeignKeyField(
        'models.WorkerInThread', related_name='bets')
    bet = fields.DecimalField(**DECIMAL_CONFIG)
    result = fields.DecimalField(**DECIMAL_CONFIG)
    currency = fields.CharField(max_length=16)
    bookmaker: fields.ForeignKeyRelation[Bookmaker] = fields.ForeignKeyField(
        'models.Bookmaker', related_name='bets')

    class Meta:
        table = "bets_log"

    def __repr__(self):
        return f"<BetItem id={self.id}>"

    def __str__(self):
        return (
            f"bet: {self.bet:.2f} {self.currency} "
            f"result: {self.result:.2f} {self.currency}. "
            f"bet ID: {self.id}"
        )

    async def get_full_printable(self):
        await self.fetch_related("worker_thread__worker")
        user = self.worker_thread.worker
        bookmaker = await self.bookmaker
        return (
            f"bet ID {self.id} от {user.mention_link} "
            f"at the bookmaker \"{bookmaker.name if bookmaker else 'unknown'}\": "
            f"{self.bet:.2f} {self.currency}, "
            f"result: {self.result:.2f} {self.currency}"
        )
