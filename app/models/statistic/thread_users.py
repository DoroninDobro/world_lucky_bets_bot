import typing
from dataclasses import dataclass
from datetime import date


convert = {True: "+", False: "-", None: "?"}


@dataclass
class ThreadUsers:
    day_name: typing.ClassVar = "Дата"
    day: date
    id_name: typing.ClassVar = "Номер матча"
    id: int
    user_names: list[str]
    user_has_worked: list[bool]

    def get_captions(self) -> list[str]:
        return [
            self.day_name,
            self.id_name,
            *self.user_names,
        ]

    def get_printable(self) -> list[str]:
        return [
            self.day.isoformat(),
            self.id,
            *list(map(convert.get, self.user_has_worked))
        ]
