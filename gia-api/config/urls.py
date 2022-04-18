from decorator_include import decorator_include
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

urlpatterns = [
    path("", decorator_include(never_cache, "django_prometheus.urls")),
    path("", include(("apps.rcoi.urls", "apps.rcoi"), namespace="rcoi")),
    path("api/v1/", include(("apps.api.v1.urls", "apps.api.v1"), namespace="apiv1")),
    path(settings.ADMIN_URL, admin.site.urls),
    # This urls used in mail templates
    re_path(
        r"^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        TemplateView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        r"^registration/confirm-email/(?P<key>[-:\w]+)/$",
        TemplateView.as_view(),
        name="account_confirm_email",
    ),
]

if settings.DEBUG:  # pragma: no cover
    from django.views import defaults

    urlpatterns += [
        path(
            "400/",
            defaults.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            defaults.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            defaults.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", defaults.server_error),
    ]

    if settings.DEBUG_TOOLBAR:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
