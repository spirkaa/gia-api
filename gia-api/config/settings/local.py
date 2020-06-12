from .common import *  # noqa

TIME_ZONE = env.str("TZ", default="Europe/Moscow")

SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY", default="pdl(ek6_-@%=a!r^=vjbpagn+^duc6q7u4v#ye3j9yfj#=8(t0"
)

DJMAIL_REAL_BACKEND = env.str(
    "DJANGO_DJMAIL_REAL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

if DEBUG and DEBUG_TOOLBAR:
    # django-debug-toolbar
    # ------------------------------------------------------------------------------
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    INTERNAL_IPS = type(str("c"), (), {"__contains__": lambda *a: True})()

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel",],
        "SHOW_TEMPLATE_CONTEXT": True,
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }
