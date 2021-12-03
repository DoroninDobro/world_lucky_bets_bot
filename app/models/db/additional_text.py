from tortoise import fields
from tortoise.models import Model


class AdditionalText(Model):
    id = fields.IntField(pk=True)
    thread = fields.ForeignKeyField(
        'models.WorkThread', related_name='additional_texts')
    is_draft = fields.BooleanField(default=True)
    is_disinformation = fields.BooleanField(default=False)
    text = fields.CharField(4096)
    send_to_workers: fields.ReverseRelation['SendWorkers']

    class Meta:
        table = "additional_texts"

    def __repr__(self):
        return f"<AdditionalText id={self.id}>"

    def get_thread_id(self):
        return self.thread_id
