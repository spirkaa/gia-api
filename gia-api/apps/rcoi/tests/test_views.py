import pytest
from ddf import G
from django.contrib.messages import get_messages
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


@pytest.mark.parametrize(
    "model_name",
    [
        "employee",
        "organisation",
        "place",
        "exam",
    ],
)
def test_view_model_list_custom(client, model_name):
    """
    Test View - Model List View (custom)
    """
    url = reverse(f"rcoi:{model_name}")
    resp = client.get(url)
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "model_name",
    [
        "date",
        "level",
        "position",
    ],
)
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
    url = reverse(
        "rcoi:date_detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_level_detail(client):
    """
    Test View - Level - Detail
    """
    obj = G(models.Level)
    url = reverse(
        "rcoi:level_detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_organisation_detail(client):
    """
    Test View - Organisation - Detail
    """
    obj = G(models.Organisation)
    url = reverse(
        "rcoi:organisation_detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_position_detail(client):
    """
    Test View - Position - Detail
    """
    obj = G(models.Position)
    url = reverse(
        "rcoi:position_detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_employee_detail(client):
    """
    Test View - Employee - Detail
    """
    obj = G(models.Employee)
    url = reverse(
        "rcoi:employee_detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_place_detail(client):
    """
    Test View - Place - Detail
    """
    name = "test place"
    place = G(models.Place, name=name)
    G(models.Exam, place=place)
    url = reverse(
        "rcoi:place_detail",
        args=[
            place.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200
    assert bytes(name, "utf-8") in resp.content
    assert len(resp.context["table"].paginated_rows) == 1


def test_view_place_detail_404(client):
    """
    Test View - Place - Detail (not found)
    """
    url = reverse(
        "rcoi:place_detail",
        args=[
            777,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 404


def test_view_exam_detail(client):
    """
    Test View - Exam - Detail
    """
    obj = G(models.Exam)
    url = reverse(
        "rcoi:exam_detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_admin_clear_caches_post(admin_client):
    """
    Test View - Admin Clear Caches (post)
    """
    url = reverse("rcoi:clear_caches")
    resp = admin_client.post(url)
    assert resp.status_code == 302
    assert resp.url == reverse("admin:index")


def test_view_admin_clear_caches_get(admin_client):
    """
    Test View - Admin Clear Caches (get - do nothing)
    """
    url = reverse("rcoi:clear_caches")
    resp = admin_client.get(url)
    assert resp.status_code == 302
    assert resp.url == reverse("admin:index")


@pytest.mark.parametrize(
    "return_value, message",
    [[True, "База данных обновлена!"], [False, "Изменений нет!"]],
)
def test_view_admin_update_db_post(admin_client, mocker, return_value, message):
    """
    Test View - Admin Update DB (post)
    """
    mocker.patch("apps.rcoi.models.RcoiUpdater.__init__", lambda x: None)
    mocker.patch("apps.rcoi.models.RcoiUpdater.run", return_value=return_value)
    url = reverse("rcoi:update_db")
    resp = admin_client.post(url)
    all_messages = list(get_messages(resp.wsgi_request))
    assert all_messages[0].message == message
    assert resp.status_code == 302
    assert resp.url == reverse("admin:index")
    mocker.resetall()


def test_view_admin_update_db_get(admin_client):
    """
    Test View - Admin Update DB (get - do nothing)
    """
    url = reverse("rcoi:update_db")
    resp = admin_client.get(url)
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


def test_view_sitemap_index(mocker, client):
    """
    Test View - sitemap index
    """
    mocker.patch("apps.rcoi.sitemap.EmployeeSitemap.limit", 1)
    G(models.Employee, n=2)
    url = reverse("rcoi:sitemap")
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"p=2" in resp.content


@pytest.mark.parametrize("section", ["employee", "organisation", "place", "static"])
def test_view_sitemap_section(client, section):
    """
    Test View - sitemap section
    """
    G(models.Exam)
    url = reverse(
        "rcoi:sitemap_section",
        args=[
            section,
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_sitemap_section_404(client):
    """
    Test View - sitemap section (not found)
    """
    url = reverse(
        "rcoi:sitemap_section",
        args=[
            "test",
        ],
    )
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.parametrize("page_num", [100, "one"])
def test_view_sitemap_section_page_404(client, page_num):
    """
    Test View - sitemap page (not found)
    """
    url = reverse(
        "rcoi:sitemap_section",
        args=[
            "employee",
        ],
    )
    resp = client.get(url, {"p": page_num})
    assert resp.status_code == 404
