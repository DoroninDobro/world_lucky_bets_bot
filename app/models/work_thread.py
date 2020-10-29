import functools

from tortoise import fields
from tortoise.models import Model

from .user import User
from ..utils.exceptions import ThreadStopped


class WorkThread(Model):
    id = fields.IntField(pk=True)
    start_photo_file_id = fields.CharField(128)
    start_message_id = fields.IntField(null=True)
    log_chat_message_id = fields.IntField(null=True)
    workers_chat_message_id = fields.IntField(null=True)
    admin: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', related_name='admin_threads')
    # noinspection PyUnresolvedReferences
    workers: fields.ReverseRelation['WorkerInThread']
    # noinspection PyUnresolvedReferences
    additional_texts: fields.ReverseRelation['AdditionalText']
    stopped: bool = fields.BooleanField(default=False)

    class Meta:
        table = "work_threads"

    def __repr__(self):
        return f"<WorkThread id={self.id}>"


def check_thread_running(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        thread = kwargs['thread']
        if thread.stopped:
            # noinspection PyUnresolvedReferences
            admin_id = thread.admin_id
            raise ThreadStopped(user_id=admin_id, thread_id=thread.id)
        await func(*args, **kwargs)
    return wrapped
