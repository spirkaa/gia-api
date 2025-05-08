import json
from http import HTTPStatus

import pytest
from ddf import G
from django.urls import reverse

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_api_subscription_add(client, authenticated_user):
    """
    Test API - Subscription - Add
    """
    auth_header = authenticated_user["auth_header"]

    employee = G(models.Employee)
    G(
        models.Exam,
        employee=employee,
    )

    url = reverse("apiv1:subscription-list")
    resp = client.post(
        url,
        data={"employee": employee.pk},
        HTTP_AUTHORIZATION=f"{auth_header}",
    )
    content = json.loads(resp.content)
    assert resp.status_code == HTTPStatus.CREATED
    assert content["employee"] == employee.pk


def test_api_subscription_add_fail(client, authenticated_user):
    """
    Test API - Subscription - Add (fail when already exists)
    """
    auth_header = authenticated_user["auth_header"]
    user = models.User.objects.get(pk=authenticated_user["user"]["pk"])

    employee = G(models.Employee)
    G(
        models.Exam,
        employee=employee,
    )
    G(models.Subscription, user=user, employee=employee)

    url = reverse("apiv1:subscription-list")
    resp = client.post(
        url,
        data={"employee": employee.pk},
        HTTP_AUTHORIZATION=f"{auth_header}",
    )
    content = json.loads(resp.content)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert content["non_field_errors"] == ["Вы уже подписаны на этого сотрудника"]


def test_api_subscription_add_limit(client, authenticated_user):
    """
    Test API - Subscription - Add (fail when over limit)
    """
    auth_header = authenticated_user["auth_header"]
    user = models.User.objects.get(pk=authenticated_user["user"]["pk"])

    employee = G(models.Employee)
    G(
        models.Exam,
        employee=employee,
    )
    G(models.Subscription, user=user, n=100)

    url = reverse("apiv1:subscription-list")
    resp = client.post(
        url,
        data={"employee": employee.pk},
        HTTP_AUTHORIZATION=f"{auth_header}",
    )
    content = json.loads(resp.content)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert content["non_field_errors"] == ["У вас не может быть больше 100 подписок"]


def test_api_subscription_delete(client, authenticated_user):
    """
    Test API - Subscription - Delete
    """
    auth_header = authenticated_user["auth_header"]
    user = models.User.objects.get(pk=authenticated_user["user"]["pk"])

    employee = G(models.Employee)
    G(
        models.Exam,
        employee=employee,
    )
    obj = G(models.Subscription, user=user, employee=employee)

    url = reverse(
        "apiv1:subscription-detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.delete(url, HTTP_AUTHORIZATION=f"{auth_header}")
    content = json.loads(resp.content)
    assert resp.status_code == HTTPStatus.OK
    assert content["detail"] == "ok"


def test_api_subscription_delete_fail(client, authenticated_user):
    """
    Test API - Subscription - Delete (fail when not owner)
    """
    auth_header = authenticated_user["auth_header"]

    employee = G(models.Employee)
    G(
        models.Exam,
        employee=employee,
    )
    obj = G(models.Subscription, employee=employee)

    url = reverse(
        "apiv1:subscription-detail",
        args=[
            obj.pk,
        ],
    )
    resp = client.delete(url, HTTP_AUTHORIZATION=f"{auth_header}")
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_api_subscription_view_list(client, authenticated_user):
    """
    Test API - Subscription - List View
    """
    auth_header = authenticated_user["auth_header"]
    user = models.User.objects.get(pk=authenticated_user["user"]["pk"])

    employee = G(models.Employee)
    G(
        models.Exam,
        employee=employee,
    )
    G(models.Subscription, user=user, employee=employee)

    url = reverse("apiv1:subscription-list")
    resp = client.get(url, HTTP_AUTHORIZATION=f"{auth_header}")
    content = json.loads(resp.content)
    assert resp.status_code == HTTPStatus.OK
    assert len(content["results"]) == 1


def test_api_subscription_view_list_401(client):
    """
    Test API - Subscription - List View (when unauthorized)
    """
    url = reverse("apiv1:subscription-list")
    resp = client.get(url)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
