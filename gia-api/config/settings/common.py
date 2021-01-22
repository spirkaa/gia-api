"""
Django settings for gia-api project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import datetime

import environ

ROOT_DIR = environ.Path(__file__) - 3  # (app/config/settings/common.py - 3 = app/)
APPS_DIR = ROOT_DIR.path("apps")
env = environ.Env()

DEBUG = env.bool("DJANGO_DEBUG", default=False)

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.postgres",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "bootstrap3",
    "corsheaders",
    "crispy_forms",
    "django_extensions",
    "django_filters",
    "django_tables2",
    "django_prometheus",
    "djmail",
    "drf_yasg",
    "rest_auth",
    "rest_auth.registration",
    "rest_framework",
    "rest_framework_filters",
    "rest_framework_jwt",
    "rest_framework_jwt.blacklist",
]
LOCAL_APPS = ["apps.rcoi", "apps.api.v1"]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

SITE_ID = 1

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = [
    str(APPS_DIR.path("fixtures")),
]

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "djmail.backends.async.EmailBackend"
DJMAIL_REAL_BACKEND = env.str(
    "DJANGO_DJMAIL_REAL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS", default=False)
EMAIL_PORT = env.int("DJANGO_EMAIL_PORT", default=25)
EMAIL_HOST = env.str("DJANGO_EMAIL_HOST", default="localhost")
EMAIL_HOST_USER = env.str("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("DJANGO_EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = env.str("DJANGO_DEFAULT_FROM_EMAIL", default="webmaster@localhost")
SERVER_EMAIL = env.str("DJANGO_SERVER_EMAIL", default="root@localhost")
EMAIL_SUBJECT_PREFIX = env.str("DJANGO_EMAIL_SUBJECT_PREFIX", default="[Django]") + " "

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = env.list(
    "DJANGO_ADMINS_LIST",
    default=[
        (
            env.str("DJANGO_ADMIN_NAME", default="admin"),
            env.str("DJANGO_ADMIN_MAIL", default="admin@example.com"),
        )
    ],
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": env.db_url(
        "DJANGO_DATABASE_URL", engine="django_prometheus.db.backends.postgresql"
    ),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TIME_ZONE
TIME_ZONE = env.str("TZ", default="UTC")
USE_TZ = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "ru-ru"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR.path("templates")),],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8,},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path("static")),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = env.str("DJANGO_ADMIN_URL", default="admin/")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s  [%(name)s:%(lineno)s]  %(levelname)s - %(message)s",
        },
        "simple": {"format": "%(levelname)s %(message)s",},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse",}},
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler",},
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": str(ROOT_DIR("app.log")),
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False,},
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "apps.rcoi": {
            "handlers": ["console", "file", "mail_admins"],
            "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "drf_yasg": {"handlers": ["console", "file"], "level": "INFO",},
        "": {
            "handlers": ["console", "file"],
            "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
        },
    },
}

# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_filters.backends.RestFrameworkFilterBackend",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

JWT_AUTH = {
    "JWT_ALLOW_REFRESH": False,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_AUTH_HEADER_PREFIX": "JWT",
    "JWT_PAYLOAD_HANDLER": "apps.api.v1.jwt_auth.utils.jwt_create_payload",
}

REST_USE_JWT = True
REST_SESSION_LOGIN = False
OLD_PASSWORD_FIELD_ENABLED = True

ACCOUNT_ADAPTER = "apps.api.v1.auth.adapter.AnotherDomainAccountAdapter"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_REQUIRED = False

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "LOGIN_URL": "/api/v1/auth/login",
    "LOGOUT_URL": "/api/v1/auth/logout",
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header",}
    },
}

CRISPY_TEMPLATE_PACK = "bootstrap3"

FILTERS_HELP_TEXT_FILTER = False

CORS_ALLOW_ALL_ORIGINS = True

DEBUG_TOOLBAR = env.bool("DJANGO_DEBUG_TOOLBAR", default=False)
