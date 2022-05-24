from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    iso_code: str
    symbol: str
    fullname: str
    plural_name: str
    short_name: str

    def __repr__(self):
        return f"{self.fullname} {self.symbol}"

    def __eq__(self, other: Currency):
        if not isinstance(other, Currency):
            return False
        return self.iso_code == other.iso_code

    def __hash__(self):
        return hash(self.iso_code)


@dataclass
class CurrenciesConfig:
    currencies: dict[str, Currency]
    base: str
    oer_api_token: str

    def symbol_by_code(self, code: str) -> str:
        return self.currencies[code].symbol

    @property
    def default_currency(self) -> Currency:
        return self.currencies[self.base]
