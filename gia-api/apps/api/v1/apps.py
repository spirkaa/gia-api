from django.apps import AppConfig


class Apiv1Config(AppConfig):
    """Config class for the api app."""

    default_auto_field = "django.db.models.AutoField"
    name = "apps.api.v1"
