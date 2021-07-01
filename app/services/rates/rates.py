from abc import ABC, abstractmethod

from loguru import logger

# TODO -  И ПРО ЭТО:
class Rates(ABC):
    val_chars = {
        "AUD": "A$",
        "AZN": "₼",
        "GBP": "£",
        "AMD": "֏",
        "BYN": "Br",
        "BGN": "лв",
        "BRL": "R$",
        "HUF": "ƒ",
        "HKD": "HK$",
        "DKK": "дат.kr",
        "USD": "$",
        "EUR": "€",
        "INR": "₹",
        "KZT": "₸",
        "CAD": "C$",
        "KGS": "сом",
        "CNY": "кит.¥",
        "MDL": "молд.L",
        "NOK": "норв.kr",
        "PLN": "zł",
        "RON": "рум.L",
        "SGD": "S$",
        "TJS": "смн.",
        "TRY": "₺",
        "TMT": "туркм.m",
        "UZS": "сўм",
        "UAH": "₴",
        "CZK": "Kč",
        "SEK": "шв.kr",
        "CHF": "₣",
        "ZAR": "ренд",
        "KRW": "₩",
        "JPY": "яп.¥",
        "RUB": "₽",
        "ILS": "₪",
        "SCR": " SCR",
        "AED": "Dh"
    }

    def __init__(self):
        logger.info(f'init {self.source_rates}')

    @abstractmethod
    async def get_updated_date(self):
        pass

    @property
    @abstractmethod
    def source_rates(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
