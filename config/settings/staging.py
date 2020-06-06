"""
Production Configurations
"""
import os
import socket

from .common import *  # noqa

DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# django-debug-toolbar
# ------------------------------------------------------------------------------
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INSTALLED_APPS += ['debug_toolbar']

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
# tricks to have debug toolbar when developing with docker
if os.environ.get("USE_DOCKER") == "yes":
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1"]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel",],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_TOOLBAR_CALLBACK": "config.settings.staging.show_toolbar",
}

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

STATIC_ROOT = str(ROOT_DIR("data/staging/staticfiles"))

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
# SECURE_BROWSER_XSS_FILTER = True
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# X_FRAME_OPTIONS = 'DENY'

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
# END SITE CONFIGURATION

INSTALLED_APPS += ["gunicorn", "cacheops"]

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
DJMAIL_REAL_BACKEND = env(
    "DJANGO_DJMAIL_REAL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_USE_TLS = env("DJANGO_EMAIL_USE_TLS", default=True)
EMAIL_HOST = env("DJANGO_EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("DJANGO_EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD")
SERVER_EMAIL = DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES["default"] = env.db("DATABASE_URL")

# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("CACHE_URL", default="redis://127.0.0.1:6379"),
        # 'TIMEOUT': 600,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,  # mimics memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        },
    }
}

CACHEOPS_REDIS = env("CACHE_URL")

CACHEOPS_DEFAULTS = {"timeout": 60 * 60 * 24}

CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 15},
    "auth.*": {"ops": ("fetch", "get")},
    "auth.permission": {"ops": "all"},
    "*.*": {"ops": "all"},
    # '*.*': {},
}

CACHEOPS_DEGRADE_ON_FAILURE = True

CACHE_MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.rcoi.middleware.SetBrowserCacheTimeoutMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django_brotli.middleware.BrotliMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
]
MIDDLEWARE = MIDDLEWARE[:1] + CACHE_MIDDLEWARE + MIDDLEWARE[1:]
MIDDLEWARE.append("django.middleware.cache.FetchFromCacheMiddleware")

CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24

RESPONSE_CACHE_SECONDS = 60

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Custom Admin URL, use {% url 'admin:index' %}
ADMIN_URL = env("DJANGO_ADMIN_URL")
