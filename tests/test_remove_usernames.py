import pytest

from app.utils.text_utils import remove_usernames


fixtures = [
    ("some text",                                  "some text"),
    ("some @bomzheg text",                         "some ... text"),
    ("some @bomzheg @bomzheg text",                "some ... ... text"),
    ("some @bomzheg @TreeHouseTrip text",          "some ... ... text"),
    ("some @bomzheg @TreeHouseTrip @bomzheg text", "some ... ... ... text"),
    ("some text @bomzheg",                         "some text ..."),
    ("some bomzheg@gmail.com text",                "some ... text"),
]


@pytest.mark.parametrize("text, expected", fixtures)
def test_remove_usernames(text: str, expected: str):
    assert remove_usernames(text) == expected
