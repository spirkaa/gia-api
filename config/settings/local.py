"""
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
"""

import os
import socket

from .common import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="pdl(ek6_-@%=a!r^=vjbpagn+^duc6q7u4v#ye3j9yfj#=8(t0"
)

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INSTALLED_APPS += ["debug_toolbar"]

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
# DJMAIL_REAL_BACKEND = env('DJANGO_DJMAIL_REAL_BACKEND',
#                           default='django.core.mail.backends.smtp.EmailBackend')
# EMAIL_USE_TLS = env('DJANGO_EMAIL_USE_TLS', default=True)
# EMAIL_HOST = env('DJANGO_EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = env('DJANGO_EMAIL_PORT', default=587)
# EMAIL_HOST_USER = env('DJANGO_EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD')
# SERVER_EMAIL = DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# CACHING
# ------------------------------------------------------------------------------
# CACHE_MIDDLEWARE = [
#     'django.middleware.cache.UpdateCacheMiddleware',
#     'django.middleware.http.ConditionalGetMiddleware'
#     ]
# MIDDLEWARE = MIDDLEWARE[:1] + CACHE_MIDDLEWARE + MIDDLEWARE[1:]
# MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')
#
# CACHE_MIDDLEWARE_SECONDS = 600

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2", "192.168.99.1"]
# tricks to have debug toolbar when developing with docker
if os.environ.get("USE_DOCKER") == "yes":
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1"]

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel",],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Your local stuff: Below this line define 3rd party library settings

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
