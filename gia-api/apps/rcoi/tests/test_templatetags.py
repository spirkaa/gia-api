import pytest

from apps.rcoi.templatetags import rupluralize


@pytest.mark.parametrize(
    "value, assertion",
    [
        ("1", "проверка"),
        ("2", "проверки"),
        ("5", "проверок"),
    ],
)
def test_rupluralize(value, assertion):
    assert rupluralize.rupluralize(value, "проверка,проверки,проверок") == assertion
