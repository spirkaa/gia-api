import pytest
from ddf import G
from django.urls import reverse

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_view_home(client):
    """
    Test View - Home
    """
    url = reverse("rcoi:home")
    resp = client.get(url)
    assert resp.status_code == 200


@pytest.mark.parametrize("model_name", ["employee", "place", "exam",])
def test_view_model_list_custom(client, model_name):
    """
    Test View - Model List View (custom)
    """
    url = reverse(f"rcoi:{model_name}")
    resp = client.get(url)
    assert resp.status_code == 200


@pytest.mark.parametrize("model_name", ["date", "level", "organisation", "position",])
def test_view_model_list_view(model_name, client):
    """
    Test View - Model List View
    """
    url = reverse(f"rcoi:{model_name}_list")
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_date_detail(client):
    """
    Test View - Date - Detail
    """
    obj = G(models.Date)
    url = reverse("rcoi:date_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_level_detail(client):
    """
    Test View - Level - Detail
    """
    obj = G(models.Level)
    url = reverse("rcoi:level_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_organisation_detail(client):
    """
    Test View - Organisation - Detail
    """
    obj = G(models.Organisation)
    url = reverse("rcoi:organisation_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_position_detail(client):
    """
    Test View - Position - Detail
    """
    obj = G(models.Position)
    url = reverse("rcoi:position_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_employee_detail(client):
    """
    Test View - Employee - Detail
    """
    obj = G(models.Employee)
    url = reverse("rcoi:employee_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_place_detail(client):
    """
    Test View - Place - Detail
    """
    obj = G(models.Place)
    url = reverse("rcoi:place_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_exam_detail(client):
    """
    Test View - Exam - Detail
    """
    obj = G(models.Exam)
    url = reverse("rcoi:exam_detail", args=[obj.pk,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_clear_caches(admin_client):
    """
    Test View - Admin Clear Caches
    """
    url = reverse("rcoi:clear_caches")
    resp = admin_client.post(url)
    assert resp.status_code == 302
    assert resp.url == reverse("admin:index")


def test_view_robotstxt(client):
    """
    Test View - robots.txt
    """
    url = reverse("rcoi:robotstxt")
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"Sitemap:" in resp.content


def test_view_sitemap(client):
    """
    Test View - sitemap
    """
    url = reverse("rcoi:sitemap")
    resp = client.get(url)
    assert resp.status_code == 200


@pytest.mark.parametrize("section", ["employee", "organisation", "static"])
def test_view_sitemap_section(client, section):
    """
    Test View - sitemap section
    """
    url = reverse("rcoi:sitemap_section", args=[section,])
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_sitemap_section_404(client):
    """
    Test View - sitemap section (not found)
    """
    url = reverse("rcoi:sitemap_section", args=["test",])
    resp = client.get(url)
    assert resp.status_code == 404
