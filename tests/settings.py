"""
Django settings for tests.
"""
import logging

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+7y-ny9+un-bv60)6d^-1n-4ozv4p3bup9sl5$v24@0m5yh7n@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_scim',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

logging.disable(logging.CRITICAL)

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

# Speed up tests with noop password hasher
PASSWORD_HASHERS = ('tests.hashers.NoopPasswordHasher',)


# -- Django SCIM specific settings --

SCIM_SERVICE_PROVIDER = {
    'USER_FILTER_PARSER': 'tests.filters.UserFilterQuery',
    'GROUP_FILTER_PARSER': 'tests.filters.GroupFilterQuery',
    'NETLOC': 'localhost',
    'AUTHENTICATION_SCHEMES': [
        {
            'type': 'oauth2',
            'name': 'OAuth 2',
            'description': 'Oauth 2 implemented with bearer token',
            'specUri': '',
            'documentationUri': '',
        },
    ],
}
