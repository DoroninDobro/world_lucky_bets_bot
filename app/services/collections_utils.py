from typing import TypeVar, Any


T = TypeVar('T')


def get_first_dict_value(d: dict[Any, T]) -> T:
    return next(iter(d.values()))