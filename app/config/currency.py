from dataclasses import dataclass
from typing import Dict


@dataclass
class Currency:
    iso_code: str
    symbol: str
    fullname: str
    plural_name: str
    short_name: str

    def __repr__(self):
        return f"{self.fullname} {self.symbol}"


def load_currency(dumped: dict) -> Dict[str: Currency]:
    """
    :param dumped: dictionary loaded from config file
    :return: dict with key - iso code and value dataclass Currency
    """
    return {currency_code: Currency(
        iso_code=currency_code,
        symbol=currency_description['symbol'],
        fullname=currency_description['fullname'],
        plural_name=currency_description['plural_name'],
        short_name=currency_description['short_name'],
    ) for currency_code, currency_description in dumped.items()}
