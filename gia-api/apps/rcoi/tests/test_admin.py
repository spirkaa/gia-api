import datetime

import pytest
from ddf import G
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_exam_import_get(admin_client):
    """
    Test Exam Import Admin View - get
    :param admin_client:
    :param mocker_exam_importer:
    :return:
    """
    date = G(models.Date, date=datetime.date(2019, 6, 5))
    url = reverse("admin:exam_import")
    resp = admin_client.get(url)
    content = resp.content

    assert resp.status_code == 200
    assert bytes(date.__str__(), "utf-8") in content


def test_exam_import_post(admin_client, mocker_exam_importer):
    """
    Test Exam Import Admin View - post (form)
    :param admin_client:
    :param mocker_exam_importer:
    :return:
    """
    date = G(models.Date, date=datetime.date(2020, 6, 1))
    level = G(models.Level, level=123)
    url = reverse("admin:exam_import")
    data = {
        "date": date.pk,
        "level": level.pk,
        "datafile_url": "http://rcoi.mcko.ru/file_test.xlsx",
    }
    resp = admin_client.post(url, data=data)
    all_messages = list(get_messages(resp.wsgi_request))

    assert resp.status_code == 302
    assert all_messages[0].message == "Файл file_test.xlsx обработан"
    assert resp.url == reverse("admin:rcoi_exam_changelist")


@pytest.mark.parametrize(
    "datafile_url, assertion",
    [
        ("http://rcoi.mcko.ru/wrong_ext.zip", "Ссылка должна заканчиваться"),
        ("http://test.com/file_test.xlsx", "Ссылка должна вести на сайт"),
    ],
)
def test_exam_import_post_fail(
    admin_client, mocker_exam_importer, datafile_url, assertion
):
    """
    Test Exam Import Admin View - post (form)
    :param admin_client:
    :param mocker_exam_importer:
    :return:
    """
    date = G(models.Date, date=datetime.date(2020, 6, 1))
    level = G(models.Level, level=123)
    url = reverse("admin:exam_import")
    data = {"date": date.pk, "level": level.pk, "datafile_url": datafile_url}
    resp = admin_client.post(url, data=data)

    assert resp.status_code == 200
    assert bytes(assertion, "utf-8") in resp.content
