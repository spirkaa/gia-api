from allauth.account.utils import user_pk_to_url_str
from dj_rest_auth.serializers import PasswordResetSerializer
from django.urls import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.api.v1.account.adapter import build_absolute_uri


def sites_domain_url_generator(request, user, temp_key):
    """Generate password reset URL using the Site domain."""
    path = reverse(
        "password_reset_confirm",
        args=[user_pk_to_url_str(user), temp_key],
    )

    url = build_absolute_uri(None, path)
    return url.replace("%3F", "?")


class SitesDomainPasswordResetSerializer(PasswordResetSerializer):
    """Custom password reset serializer using Site domain for URLs."""

    def get_email_options(self):
        return {"url_generator": sites_domain_url_generator}


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """TokenObtainPairSerializer with username and email."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.get_username()
        token["email"] = user.email

        return token
