from decimal import Decimal

from aiogram import types
from aiogram.utils.markdown import hlink, quote_html
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from .common import DECIMAL_CONFIG
from app.models.enum.salary_type import SalaryType
from app.view.common import USER_STATUS_NAME


class User(Model):
    id = fields.BigIntField(pk=True, generated=False)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    is_bot: bool = fields.BooleanField(null=True)
    registered: bool = fields.BooleanField(null=False, default=False)
    worker_status = fields.CharEnumField(SalaryType, null=True)
    piecework_pay = fields.DecimalField(**DECIMAL_CONFIG, null=True)
    salary = fields.TextField(null=True)
    work_threads: fields.ReverseRelation['WorkerInThread']  # noqa F821
    admin_threads: fields.ReverseRelation['WorkThread']  # noqa F821
    balance_events: fields.ReverseRelation['BalanceEvents']  # noqa F821
    balance_events_author: fields.ReverseRelation['BalanceEvents']  # noqa F821

    class Meta:
        table = "users"

    @classmethod
    async def create_from_tg_user(cls, user: types.User):
        user = await cls.create(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_bot=user.is_bot
        )

        return user

    async def update_user_data(self, user_tg):
        # TODO изучить фреймворк лучше - уверен есть встроенная функция для обновления только в случае расхождений
        changed = False

        if self.id is None and user_tg.id is not None:
            changed = True
            self.id = user_tg.id

        if user_tg.first_name is not None:
            if self.first_name != user_tg.first_name:
                changed = True
                self.first_name = user_tg.first_name

            if self.last_name != user_tg.last_name:
                changed = True
                self.last_name = user_tg.last_name

            if self.username != user_tg.username:
                changed = True
                self.username = user_tg.username
            if self.is_bot is None and user_tg.is_bot is not None:
                changed = True
                self.is_bot = user_tg.is_bot

        if changed:
            await self.save()

    @classmethod
    async def get_or_create_from_tg_user(cls, user_tg: types.User):

        try:
            user = await cls.get(id=user_tg.id)
        except DoesNotExist:
            return await cls.create_from_tg_user(user=user_tg)
        else:
            await user.update_user_data(user_tg)
        return user

    @property
    def mention_link(self):
        return hlink(self.fullname, f"tg://user?id={self.id}")

    @property
    def mention_no_link(self):
        if self.username:
            rez = hlink(self.fullname, f"t.me/{self.username}")
        else:
            rez = quote_html(self.fullname)
        return rez

    @property
    def fullname(self):
        if self.last_name is not None:
            return ' '.join((self.first_name, self.last_name))
        return self.first_name or self.username or str(self.id)

    @property
    def render_salary(self) -> str:
        result = USER_STATUS_NAME[self.worker_status]
        match self.worker_status:
            case None:
                return result
            case SalaryType.SALARY:
                return f"{result} {self.salary}"
            case SalaryType.BET_PERCENT:
                return f"{result} {self.piecework_pay:.2f}%"
            case SalaryType.WIN_PERCENT:
                return f"{result} {self.piecework_pay:.2f}%"

    def calculate_piecework(self, total: Decimal) -> Decimal:
        assert self.worker_status in (SalaryType.BET_PERCENT, SalaryType.WIN_PERCENT)
        return total * (self.piecework_pay / 100)

    def __str__(self):
        rez = (
            f"{self.mention_link}\n"
            f"#️⃣{self.id}\n"
        )
        if self.username:
            rez += f"username @{self.username}\n"
        return rez

    def __repr__(self):
        return str(self)
