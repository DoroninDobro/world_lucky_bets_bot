from app.models.db import User
from app.services.reports.common import excel_bets_caption_name


def test_excel_caption_name():
    words_pairs = (
        ("python", "python"),
        ("PyThOn", "PyThOn"),
        ("p[y]t/h\\o?n", "python"),
        ("42", "42"),
        ("this is wherry long name, so long so it does not have any limit", "this is wherry long name, so lon"),
    )
    for fixture, expected in words_pairs:
        assert excel_bets_caption_name(User(first_name=fixture)) == expected
