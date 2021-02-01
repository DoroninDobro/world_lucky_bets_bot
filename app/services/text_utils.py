from decimal import Decimal, InvalidOperation


def parse_numeric(text: str) -> Decimal:
    text = text.replace(",", ".")
    try:
        result = Decimal(text)
        int(result)  # Check that it is not "inf" or "nan"
    except (ValueError, OverflowError, InvalidOperation) as e:
        raise ValueError from e
    return result
