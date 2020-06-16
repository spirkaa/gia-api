import pytest
from ddf import G
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_jwt.settings import api_settings

User = get_user_model()


@pytest.fixture
def authenticated_user(client):
    prefix = api_settings.JWT_AUTH_HEADER_PREFIX
    user_data = {
        "email": "test@test.com",
        "password": "3HAKNaZT5eRq5L",
        "first_name": "First",
        "last_name": "Last",
    }
    user = G(User, **user_data)
    user.set_password(user_data["password"])
    user.save()
    url = reverse("apiv1:rest_login")
    resp = client.post(url, data=user_data)
    resp.data["auth_header"] = f"{prefix} {resp.data['token']}"
    return resp.data
