"""
Django settings for randomlunch project.

Import from local settings
Needed for Heroku deployment
    tuto here: https://djangogirls.gitbooks.io/django-girls-tutorial-extensions/content/heroku/
"""

import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite')
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

DEBUG = False

try:
    from .local_settings import *
except ImportError:
    pass