import pytest
from ddf import G

from apps.rcoi import models
from apps.rcoi.filters import SearchVectorFilter

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "name, query", [("первая", "первый"), ("проверка", "успешные проверки функций")]
)
def test_search_vector_filter(name, query):
    """
    Test full text search
    """
    G(models.Place, name=name)
    G(models.Place, name=f"школа {name}")

    qs = models.Place.objects.all()
    f = SearchVectorFilter(search_fields=["search_vector"])

    # no filter
    res = f.filter(qs, "")
    assert res == qs
    assert res.count() == 2

    # only 1 of 2 records match
    res = f.filter(qs, "школа")
    assert res.count() == 1

    # all records match
    res = f.filter(qs, query)
    assert res.count() == 2
