import typing
from dataclasses import dataclass
from datetime import date
from typing import Union

from app.models import WorkThread

convert = {True: "+", False: "-", None: "?"}


@dataclass
class ThreadUsers:
    day_name: typing.ClassVar = "Date"
    day: date
    thread_id_name: typing.ClassVar = "Match number"
    thread_name_name: typing.ClassVar = "Match name"
    thread: WorkThread
    user_names: list[str]
    user_has_worked: list[bool]

    def get_captions(self) -> list[str]:
        return [
            self.day_name,
            self.thread_id_name,
            self.thread_name_name,
            *self.user_names,
        ]

    def get_printable(self) -> list[Union[str, date]]:
        return [
            self.day,
            self.thread.id,
            self.thread.name,
            *list(map(convert.get, self.user_has_worked))
        ]
