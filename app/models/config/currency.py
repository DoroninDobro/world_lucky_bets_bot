from dataclasses import dataclass


@dataclass
class Currency:
    iso_code: str
    symbol: str
    fullname: str
    plural_name: str
    short_name: str

    def __repr__(self):
        return f"{self.fullname} {self.symbol}"


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
