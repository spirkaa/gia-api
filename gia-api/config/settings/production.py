from .common import *  # noqa

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
POD_IP = env.str("POD_IP", default=None)
if POD_IP:
    ALLOWED_HOSTS.append(POD_IP)

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

INSTALLED_APPS += ["gunicorn", "cacheops"]
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy
USE_X_FORWARDED_HOST = env.bool("DJANGO_USE_X_FORWARDED_HOST", default=False)
SECURE_PROXY_SSL_HEADER = env.tuple(
    "DJNAGO_SECURE_PROXY_SSL_HEADER", default=("HTTP_X_FORWARDED_PROTO", "https")
)
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
)
SECURE_BROWSER_XSS_FILTER = env.bool("DJANGO_SECURE_BROWSER_XSS_FILTER", default=True)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
SESSION_COOKIE_HTTPONLY = env.bool("DJANGO_SESSION_COOKIE_HTTPONLY", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
CSRF_COOKIE_HTTPONLY = env.bool("DJANGO_CSRF_COOKIE_HTTPONLY", default=True)
X_FRAME_OPTIONS = env.str("DJNAGO_X_FRAME_OPTIONS", default="DENY")

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
DJMAIL_REAL_BACKEND = env.str(
    "DJANGO_DJMAIL_REAL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS", default=True)
EMAIL_PORT = env.int("DJANGO_EMAIL_PORT", default=587)
DEFAULT_FROM_EMAIL = env.str("DJANGO_DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
SERVER_EMAIL = env.str("DJANGO_SERVER_EMAIL", default=EMAIL_HOST_USER)

# CACHING
# ------------------------------------------------------------------------------
CACHE_MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.rcoi.middleware.SetBrowserCacheTimeoutMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django_brotli.middleware.BrotliMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
]
MIDDLEWARE = MIDDLEWARE[:2] + CACHE_MIDDLEWARE + MIDDLEWARE[2:]
MIDDLEWARE = (
    MIDDLEWARE[:-1]
    + ["django.middleware.cache.FetchFromCacheMiddleware"]
    + MIDDLEWARE[-1:]
)

CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": env.str("DJANGO_CACHE_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

CACHEOPS_REDIS = env.str("DJANGO_CACHE_URL")
CACHEOPS_DEFAULTS = {"timeout": 60 * 60 * 24}
CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 15},
    "auth.*": {"ops": ("fetch", "get")},
    "auth.permission": {"ops": "all"},
    "rcoi.*": {"ops": "all"},
    "*.*": {},
}
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_LRU = True

# TTL of cached response in backend storage
CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24
# TTL of cache on client (cache-control: max-age)
RESPONSE_CACHE_SECONDS = 60 * 10
