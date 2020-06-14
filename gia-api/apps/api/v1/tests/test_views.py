import json

import pytest
from ddf import G
from django.urls import reverse

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_api_view_root(client):
    """
    Test API - Root View
    """
    url = reverse("apiv1:api-root")
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_filter_employee_list(client):
    """
    Test API - Employee - Filter by CSV of ids
    """
    obj1, obj2, obj3 = G(models.Employee, n=3)
    url = reverse("apiv1:employee-list")
    resp = client.get(url, {"id": f"{obj1.pk},{obj2.pk},{obj3.pk}",})
    content = json.loads(resp.content)
    print(content)
    assert resp.status_code == 200
    assert content["count"] == 3


@pytest.mark.parametrize(
    "view_name",
    [
        "date",
        "level",
        "organisation",
        "position",
        "employee",
        "place",
        "exam",
        "flat",
        "full",
        "datasource",
        "datafile",
    ],
)
def test_api_view_list(client, view_name):
    """
    Test API - List Views
    """
    url = reverse(f"apiv1:{view_name}-list")
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_date_view_detail(client):
    """
    Test API - Date - Detail View
    """
    obj = G(models.Date)
    url = reverse("apiv1:date-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_level_view_detail(client):
    """
    Test API - Level - Detail View
    """
    obj = G(models.Level)
    url = reverse("apiv1:level-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_organisation_view_detail(client):
    """
    Test API - Organisation- Detail View
    """
    obj = G(models.Organisation)
    url = reverse("apiv1:organisation-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_position_view_detail(client):
    """
    Test API - Position - Detail View
    """
    obj = G(models.Position)
    url = reverse("apiv1:position-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_employee_view_detail(client):
    """
    Test API - Employee - Detail View
    """
    obj = G(models.Employee)
    url = reverse("apiv1:employee-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_place_view_detail(client):
    """
    Test API - Place - Detail View
    """
    obj = G(models.Place)
    url = reverse("apiv1:place-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_exam_view_detail(client):
    """
    Test API - Exam - Detail View (Default Serializer)
    """
    obj = G(models.Exam)
    url = reverse("apiv1:exam-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_examflat_view_detail(client):
    """
    Test API - Exam - Detail View (Flat Serializer)
    """
    obj = G(models.Exam)
    url = reverse("apiv1:flat-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_examfull_view_detail(client):
    """
    Test API - Exam - Detail View (Full Serializer)
    """
    obj = G(models.Exam)
    url = reverse("apiv1:full-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_datasource_view_detail(client):
    """
    Test API - DataSource - Detail View
    """
    obj = G(models.DataSource)
    url = reverse("apiv1:datasource-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_api_datafile_view_detail(client):
    """
    Test API - DataFile - Detail View
    """
    obj = G(models.DataFile)
    url = reverse("apiv1:datafile-detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200
