from decimal import Decimal, InvalidOperation


def remove_usernames(text: str) -> str:
    usernames = [word for word in text.split() if "@" in word]
    for username in usernames:
        text = text.replace(username, "...")
    return text


def parse_numeric(text: str) -> Decimal:
    text = text.replace(",", ".")
    try:
        result = Decimal(text)
        int(result)  # Check that it is not "inf" or "nan"
    except (ValueError, OverflowError, InvalidOperation) as e:
        raise ValueError from e
    return result
