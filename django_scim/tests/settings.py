SECRET_KEY=1234567890
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_database',
    }
}
ROOT_URLCONF = 'tests.urls'

#DJANGO_SCIM_SCHEME = 'http'  # for debugging
DJANGO_SCIM_NETLOC = 'localhost'
#DJANGO_SCIM_AUTH_BACKENDS = []
#DJANGO_SCIM_BASE_URL = '/scim/v2/'
#DJANGO_SCIM_BASE_URL_REGEX = r'^scim/v2/'

