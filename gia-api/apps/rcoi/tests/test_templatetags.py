import pytest

from apps.rcoi.templatetags import navactive, rupluralize

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "value, assertion",
    [
        ("rcoi:exam", "active"),
        ("rcoi:place", ""),
    ],
)
def test_navactive(rf, value, assertion):
    """
    Test template tag - navactive
    """
    request = rf.get("rcoi:exam")
    request.path = request.path + "/"

    assert navactive.navactive(request, value) == assertion


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
