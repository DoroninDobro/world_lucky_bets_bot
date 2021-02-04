from tortoise import fields
from tortoise.models import Model

from .work_thread import WorkThread
from .user import User


class WorkerInThread(Model):
    id = fields.IntField(pk=True)
    work_thread: fields.ForeignKeyRelation[WorkThread] = fields.ForeignKeyField(
        'models.WorkThread', related_name='workers')
    worker: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='work_threads')
    message_id: int = fields.IntField()
    # noinspection PyUnresolvedReferences
    bets: fields.ReverseRelation["BetItem"]

    class Meta:
        table = "workers_in_threads"
        unique_together = (("worker", "work_thread"),)

    def __repr__(self):
        return f"<WorkerInThread id={self.id}>"
