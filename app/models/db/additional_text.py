from tortoise import fields
from tortoise.models import Model

from .work_thread import WorkThread


class AdditionalText(Model):
    id = fields.IntField(pk=True)
    thread: fields.ForeignKeyRelation[WorkThread] = fields.ForeignKeyField(
        'models.WorkThread', related_name='additional_texts')
    is_draft: bool = fields.BooleanField(default=True)
    is_disinformation: bool = fields.BooleanField(default=False)
    text = fields.CharField(4096)
    # noinspection PyUnresolvedReferences
    send_to_workers: fields.ReverseRelation['SendWorkers']
    sent = fields.DatetimeField(null=True)

    class Meta:
        table = "additional_texts"

    def __repr__(self):
        return f"<AdditionalText id={self.id}>"

    def get_thread_id(self):
        # noinspection PyUnresolvedReferences
        return self.thread_id
