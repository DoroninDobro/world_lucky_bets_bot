import functools

from tortoise import fields
from tortoise.models import Model

from app.utils.exceptions import ThreadStopped


class WorkThread(Model):
    id = fields.IntField(pk=True)
    start = fields.DatetimeField(generated=True)
    start_photo_file_id = fields.CharField(128)
    start_message_id = fields.IntField(null=True)
    workers_chat_message_id = fields.IntField(null=True)
    admin = fields.ForeignKeyField('models.User', related_name='admin_threads')
    workers: fields.ReverseRelation['WorkerInThread']
    additional_texts: fields.ReverseRelation['AdditionalText']
    stopped = fields.BooleanField(default=False)
    name = fields.CharField(128, null=True)

    class Meta:
        table = "work_threads"

    def __repr__(self):
        return f"<WorkThread id={self.id}>"

    def get_admin_id(self):
        return self.admin_id


def check_thread_running(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        thread = kwargs['thread']
        if thread.stopped:
            raise ThreadStopped(user_id=thread.get_admin_id(), thread_id=thread.id)
        return await func(*args, **kwargs)
    return wrapped
