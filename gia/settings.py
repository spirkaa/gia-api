"""
Django settings for gia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os

from configurations import Configuration, values


class Common(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    # BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = values.BooleanValue(False)

    ALLOWED_HOSTS = []

    CRISPY_TEMPLATE_PACK = 'bootstrap3'
    FILTERS_HELP_TEXT_FILTER = False
    BOOTSTRAP3 = {

        # The URL to the jQuery JavaScript file
        'jquery_url': '/static/js/jquery.min.js',

        # The complete URL to the Bootstrap CSS file (None means derive it from base_url)
        'css_url': '/static/css/bootstrap.min.css',

        # The complete URL to the Bootstrap JavaScript file (None means derive it from base_url)
        'javascript_url': '/static/js/bootstrap.min.js',

    }
    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'debug_toolbar',
        'django_extensions',
        'django_tables2',
        'django_filters',
        'crispy_forms',
        'bootstrap3',

        'rcoi',
    ]

    MIDDLEWARE_CLASSES = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'gia.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'django.core.context_processors.request',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'gia.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/1.9/ref/settings/#databases
    DATABASES = values.DatabaseURLValue(
        'sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    )

    # Password validation
    # https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/1.9/topics/i18n/
    LANGUAGE_CODE = 'ru-ru'

    TIME_ZONE = 'Europe/Moscow'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.9/howto/static-files/
    STATIC_URL = '/static/'

    # Additional locations of static files
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s  [%(name)s:%(lineno)s]  %(levelname)s - %(message)s',
            },
            'simple': {
                'format': '%(levelname)s %(message)s',
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.path.join(PROJECT_PATH, 'logs', 'gia.log'),
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
            }
        },
        'loggers': {
            # Silence SuspiciousOperation.DisallowedHost exception ('Invalid
            # HTTP_HOST' header messages). Set the handler to 'null' so we don't
            # get those annoying emails.
            'django.security.DisallowedHost': {
                'handlers': ['null'],
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            }
        }
    }


class Development(Common):
    """
    The in-development settings and the default configuration.
    """
    DEBUG = True

    ALLOWED_HOSTS = []


class Staging(Common):
    """
    The in-staging settings.
    """
    # Security
    SESSION_COOKIE_SECURE = values.BooleanValue(True)
    SECURE_BROWSER_XSS_FILTER = values.BooleanValue(True)
    SECURE_CONTENT_TYPE_NOSNIFF = values.BooleanValue(True)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = values.BooleanValue(True)
    SECURE_HSTS_SECONDS = values.IntegerValue(31536000)
    SECURE_REDIRECT_EXEMPT = values.ListValue([])
    SECURE_SSL_HOST = values.Value(None)
    SECURE_SSL_REDIRECT = values.BooleanValue(True)
    SECURE_PROXY_SSL_HEADER = values.TupleValue(
        ('HTTP_X_FORWARDED_PROTO', 'https')
    )


class Production(Staging):
    """
    The in-production settings.
    """
    pass
