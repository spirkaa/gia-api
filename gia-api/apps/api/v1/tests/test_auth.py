import re

import pytest
from ddf import G
from django.urls import reverse

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_api_auth_register_and_mail_verify(client, mailoutbox, custom_site):
    """
    Test API - Auth - Registration, Authorization, Email Verification
    """
    # Create account
    data = {
        "email": "test@test.com",
        "password1": "3HAKNaZT5eRq5L",
        "password2": "3HAKNaZT5eRq5L",
    }
    url = reverse("apiv1:rest_register")
    resp = client.post(url, data=data)
    assert resp.status_code == 201
    assert "access_token" in resp.data
    assert len(mailoutbox) == 1
    assert data["email"] in mailoutbox[0].to
    assert custom_site["name"] in mailoutbox[0].body

    # Logout
    logout_url = reverse("apiv1:rest_logout")
    logout_resp = client.post(logout_url)
    assert logout_resp.status_code == 200
    assert "Neither cookies or blacklist are enabled" in logout_resp.data["detail"]

    # Login with new account
    auth_data = {
        "email": data["email"],
        "password": data["password1"],
    }
    auth_url = reverse("apiv1:rest_login")
    auth_resp = client.post(auth_url, data=auth_data)
    assert auth_resp.status_code == 200
    assert "access_token" in auth_resp.data

    # Verify mail
    mail_verify_link = re.search(
        rf"(https://{custom_site['domain']}.*)(?:/)", mailoutbox[0].body
    ).group(0)
    data = {"key": mail_verify_link.split("/")[-2]}
    url = reverse("apiv1:rest_verify_email")
    resp = client.post(url, data=data)
    assert resp.status_code == 200
    assert resp.data["detail"] == "ок"

    # Check mail is verified
    new_user = models.User.objects.latest("id")
    mail_verified = new_user.emailaddress_set.get(email=new_user.email).verified
    assert mail_verified is True


@pytest.mark.parametrize(
    "pass1,pass2", [("password", "password"), ("n0tMatchPass", "pAss#0tMatch")]
)
def test_api_auth_register_fail(client, pass1, pass2):
    """
    Test API - Auth - Registration failed
    """
    url = reverse("apiv1:rest_register")
    resp = client.post(
        url,
        data={
            "email": "test@test.com",
            "password1": pass1,
            "password2": pass2,
        },
    )
    assert resp.status_code == 400


def test_api_auth_login_fail(client):
    """
    Test API - Auth - Login failed
    """
    data = {
        "email": "test@test.com",
        "password": "3HAKNaZT5eRq5L",
    }
    url = reverse("apiv1:rest_login")
    resp = client.post(url, data=data)
    assert resp.status_code == 400


def test_api_auth_user_details(client, authenticated_user):
    """
    Test API - Auth - User Details View
    """
    auth_header = authenticated_user["auth_header"]
    user = authenticated_user["user"]
    url = reverse("apiv1:rest_user_details")
    resp = client.get(url, HTTP_AUTHORIZATION=f"{auth_header}")
    assert resp.status_code == 200
    assert resp.data["username"] == user["username"]
    assert resp.data["email"] == user["email"]


def test_api_auth_user_details_update(client, authenticated_user):
    """
    Test API - Auth - User Details Update
    """
    auth_header = authenticated_user["auth_header"]
    data = {
        "first_name": "New First",
        "last_name": "",
    }
    url = reverse("apiv1:rest_user_details")
    resp = client.patch(
        url,
        data=data,
        content_type="application/json",
        HTTP_AUTHORIZATION=f"{auth_header}",
    )
    assert resp.status_code == 200
    assert resp.data["first_name"] == data["first_name"]
    assert resp.data["last_name"] == data["last_name"]


def test_api_auth_password_change(client, authenticated_user):
    """
    Test API - Auth - Password Change
    """
    auth_header = authenticated_user["auth_header"]
    data = {
        "old_password": "3HAKNaZT5eRq5L",
        "new_password1": "3HAK-T5eRq5L",
        "new_password2": "3HAK-T5eRq5L",
    }
    url = reverse("apiv1:rest_password_change")
    resp = client.post(url, data=data, HTTP_AUTHORIZATION=f"{auth_header}")
    assert resp.status_code == 200
    assert resp.data["detail"] == "Новый пароль сохранён."


def test_api_auth_password_reset(client, mailoutbox, custom_site):
    """
    Test API - Auth - Password reset
    """
    # Request password reset
    data = {
        "email": "test@test.com",
    }
    G(models.User, **data)
    url = reverse("apiv1:rest_password_reset")
    resp = client.post(url, data=data)
    assert resp.status_code == 200
    assert len(mailoutbox) == 1
    assert data["email"] in mailoutbox[0].to
    assert custom_site["name"] in mailoutbox[0].body

    # Reset password
    new_data = {
        "new_password1": "3HAK-T5eRq5L",
        "new_password2": "3HAK-T5eRq5L",
    }
    reset_link = re.search(
        rf"(https://{custom_site['domain']}.*)(?:/)", mailoutbox[0].body
    ).group(0)
    uid, token = reset_link.split("/")[-3:-1]
    new_data["uid"] = uid
    new_data["token"] = token
    new_url = reverse("apiv1:rest_password_reset_confirm")
    new_resp = client.post(new_url, data=new_data)
    assert new_resp.status_code == 200
    assert new_resp.data["detail"] == "Пароль изменён на новый."

    # New password should work
    auth_data = {
        "email": data["email"],
        "password": new_data["new_password1"],
    }
    auth_url = reverse("apiv1:rest_login")
    auth_resp = client.post(auth_url, data=auth_data)
    assert auth_resp.status_code == 200
    assert "access_token" in auth_resp.data
