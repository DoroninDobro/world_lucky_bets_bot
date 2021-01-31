def parse_numeric_float(text: str):
    try:
        result = float(text)
        int(result)  # Check that it is not "inf" or "nan"
    except (ValueError, OverflowError) as e:
        raise ValueError from e
