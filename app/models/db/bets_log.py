from tortoise import fields
from tortoise.models import Model

from .workers_in_threads import WorkerInThread
from .bookmaker import Bookmaker


DECIMAL_CONFIG = dict(max_digits=12, decimal_places=4)


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
            f"ставка: {self.bet:.2f} {self.currency} "
            f"результат: {self.result:.2f} {self.currency}. "
            f"ID ставки: {self.id}"
        )

    async def get_full_printable(self):
        await self.fetch_related("worker_thread__worker")
        user = self.worker_thread.worker
        bookmaker = await self.bookmaker
        return (
            f"ставка ID {self.id} от {user.mention_link} "
            f"у букмекера \"{bookmaker.name if bookmaker else 'не известно'}\": "
            f"{self.bet:.2f} {self.currency}, "
            f"результат: {self.result:.2f} {self.currency}"
        )
