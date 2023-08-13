import pytest
from ddf import G
from django.urls import reverse

from apps.rcoi import models
from apps.rcoi.filters import SearchVectorFilter, dates_filtered_by_exams_in_place

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("name", "query"), [("первая", "первый"), ("проверка", "успешные проверки функций")]
)
def test_search_vector_filter(name, query):
    """
    Test full text search
    """
    G(models.Place, name=name)
    G(models.Place, name=f"школа {name}")

    qs = models.Place.objects.all()
    f = SearchVectorFilter(search_fields=["search_vector"])

    # special characters
    res = f.filter(qs, "\\()&!|<>:'")
    assert res.count() == 0

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


@pytest.mark.parametrize(("req", "count"), [(True, 1), (None, 3)])
def test_dates_filtered_by_exams_in_place(client, req, count):
    """
    Test dates filtered by exams in place
    """
    G(models.Date, n=count)
    date = models.Date.objects.last()

    place = G(models.Place)
    G(models.Exam, date=date, place=place)

    url = reverse("rcoi:organisation_detail", kwargs={"pk": place.id})

    if req:
        req = client.get(url)
    assert dates_filtered_by_exams_in_place(req).count() == count
