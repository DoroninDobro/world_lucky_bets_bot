import typing
from enum import Enum

from aiogram.utils.markdown import hlink, quote_html
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model


class ChatType(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = 'channel'


class Chat(Model):
    id = fields.BigIntField(pk=True, generated=False)
    type_ = typing.cast(ChatType, fields.CharEnumField(ChatType))
    title = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    description = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "chats"

    @classmethod
    async def create_from_tg_chat(cls, chat):
        chat = await cls.create(
            id=chat.id,
            type_=chat.type,
            title=chat.title,
            username=chat.username
        )
        return chat

    @classmethod
    async def get_or_create_from_tg_chat(cls, chat):
        try:
            chat = await cls.get(id=chat.id)
        except DoesNotExist:
            chat = await cls.create_from_tg_chat(chat=chat)
        return chat

    @property
    def mention(self):
        return hlink(self.title, f"t.me/{self.username}") if self.username else quote_html(self.title)

    def __str__(self):
        rez = f"Chat with type: {self.type_} with ID {self.id}, title: {self.title}"
        if self.username:
            rez += f" Username @{self.username}"
        if self.description:
            rez += f". description: {self.description}"
        return rez

    def __repr__(self):
        return str(self)
