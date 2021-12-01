from abc import ABC, abstractmethod


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
        "DKK": "danish kr",
        "USD": "$",
        "EUR": "€",
        "INR": "₹",
        "KZT": "₸",
        "CAD": "C$",
        "KGS": "сом",
        "CNY": "chinese ¥",
        "MDL": "moldovan L",
        "NOK": "Norwegian kr",
        "PLN": "zł",
        "RON": "romanian L",
        "SGD": "S$",
        "TJS": "somoni",
        "TRY": "₺",
        "TMT": "Turkmenistani manat",
        "UZS": "сўм",
        "UAH": "₴",
        "CZK": "Kč",
        "SEK": "Swedish kr",
        "CHF": "₣",
        "ZAR": "rand",
        "KRW": "₩",
        "JPY": "Japanese ¥",
        "RUB": "₽",
        "ILS": "₪",
        "SCR": " SCR",
        "AED": "Dh"
    }

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
