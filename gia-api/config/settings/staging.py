from .local import *  # noqa

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

STATIC_ROOT = str(ROOT_DIR("data/staging/staticfiles"))

INSTALLED_APPS += ["gunicorn", "cacheops"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


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

if DEBUG and DEBUG_TOOLBAR:
    # django-debug-toolbar must be after all cache
    MIDDLEWARE = (
        MIDDLEWARE[:-2]
        + ["django.middleware.cache.FetchFromCacheMiddleware"]
        + MIDDLEWARE[-2:]
    )
else:
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
CACHEOPS_DEFAULTS = {"timeout": 60 * 10}
CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 10},
    "auth.*": {"ops": ("fetch", "get")},
    "auth.permission": {"ops": "all"},
    "*.*": {"ops": "all"},
}
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_LRU = True

# TTL of cached response in backend storage
CACHE_MIDDLEWARE_SECONDS = 60 * 10
# TTL of cache on client (cache-control: max-age)
RESPONSE_CACHE_SECONDS = 60
