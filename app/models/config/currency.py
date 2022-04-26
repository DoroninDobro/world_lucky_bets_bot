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
    oer_api_token: str
