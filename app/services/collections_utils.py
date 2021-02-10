from typing import TypeVar, Any


T = TypeVar('T')


def get_first_dict_value(d: dict[Any, T]) -> T:
    try:
        return next(iter(d.values()))
    except StopIteration:
        raise IndexError("dict doesnt have any element")
