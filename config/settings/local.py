"""
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .common import *  # noqa
import socket
import os

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='pdl(ek6_-@%=a!r^=vjbpagn+^duc6q7u4v#ye3j9yfj#=8(t0')

# Mail settings
# ------------------------------------------------------------------------------

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
#                     default='django.core.mail.backends.console.EmailBackend')

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += ['debug_toolbar']

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', '192.168.99.1']
# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1]+"1"]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Your local stuff: Below this line define 3rd party library settings
