from tortoise import fields
from tortoise.models import Model

from app.models import User


class Bookmaker(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128, index=True, unique=True)
    add_by: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User', related_name='added_bookmakers')
    created = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "bookmakers"

    def __repr__(self):
        return f"<Bookmaker id={self.id} name={self.name}>"

    def __str__(self):
        return self.name
