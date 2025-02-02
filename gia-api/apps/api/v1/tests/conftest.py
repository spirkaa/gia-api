import pytest
from ddf import G
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()


@pytest.fixture
def authenticated_user(client):
    """Authenticated user fixture."""
    prefix = api_settings.AUTH_HEADER_TYPES[0]
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
    resp.data["auth_header"] = f"{prefix} {resp.data['access']}"
    return resp.data


@pytest.fixture
def custom_site():
    """Site fixture."""
    site_data = {
        "domain": "custom-domain.net",
        "name": "Custom Site Name",
    }
    Site.objects.filter(pk=1).update(**site_data)
    return site_data
