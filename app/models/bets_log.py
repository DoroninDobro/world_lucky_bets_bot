from tortoise import fields
from tortoise.models import Model

from .workers_in_threads import WorkerInThread
DECIMAL_CONFIG = dict(max_digits=12, decimal_places=4)


class BetItem(Model):
    id = fields.IntField(pk=True)
    created = fields.DatetimeField(auto_now=True)
    # noinspection PyUnresolvedReferences
    worker_thread: fields.ForeignKeyRelation[WorkerInThread] = fields.ForeignKeyField(
        'models.WorkerInThread', related_name='bets')
    bet = fields.DecimalField(**DECIMAL_CONFIG)
    result = fields.DecimalField(**DECIMAL_CONFIG)
    currency = fields.CharField(max_length=16)

    class Meta:
        table = "bets_log"

    def __repr__(self):
        return f"<BetItem id={self.id}>"

    def __str__(self):
        return f"{self.bet} {self.currency} и получил результат {self.result} {self.currency}"
