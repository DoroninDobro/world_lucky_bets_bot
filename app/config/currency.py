from typing import Any

from app.models.config.currency import Currency, CurrenciesConfig


def load_currencies(dct: dict[str, Any]) -> CurrenciesConfig:
    currencies_config = CurrenciesConfig(
        currencies=load_currency(dct["currency"]),
        oer_api_token=dct["oer_api_token"],
        base=dct["base"],
    )

    from app import constants
    constants.BASE_CURRENCY = currencies_config.base
    return currencies_config


def load_currency(dumped: dict) -> dict[str, Currency]:
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
