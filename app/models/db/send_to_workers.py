from tortoise import fields
from tortoise.models import Model

from .user import User
from .additional_text import AdditionalText


class SendWorkers(Model):
    id = fields.IntField(pk=True)
    text: fields.ForeignKeyRelation[AdditionalText] = fields.ForeignKeyField(
        'models.AdditionalText', related_name='send_to_workers')
    worker: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='send_info')
    send: bool = fields.BooleanField(default=True)

    class Meta:
        table = "send_to_workers"

    def __repr__(self):
        return f"<SendWorkers id={self.id}>"
