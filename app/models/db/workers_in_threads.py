from tortoise import fields
from tortoise.models import Model


class WorkerInThread(Model):
    id = fields.IntField(pk=True)
    work_thread = fields.ForeignKeyField(
        'models.WorkThread', related_name='workers')
    worker = fields.ForeignKeyField(
        'models.User', related_name='work_threads')
    message_id = fields.IntField()
    bets: fields.ReverseRelation["BetItem"]

    class Meta:
        table = "workers_in_threads"
        unique_together = (("worker", "work_thread"),)

    def __repr__(self):
        return f"<WorkerInThread id={self.id}>"
