from django.conf import settings
from six.moves.urllib.parse import urlunparse


BASE_SCIM_LOCATION_PARTS = (
    settings.get('DJANGO_SCIM_SCHEME', 'https'),
    settings['DJANGO_SCIM_NETLOC'],
    '',  # path
    '',  # params
    '',  # query
    ''   # fragment
)

BASE_SCIM_LOCATION = urlunparse(BASE_SCIM_LOCATION_PARTS)

DEFAULT_GROUP_MODEL_STRING = 'django.contrib.auth.models.Group'

BASE_URL = settings.get('DJANGO_SCIM_BASE_URL', '/scim/v2/')
BASE_URL_REGEX = settings.get('DJANGO_SCIM_BASE_URL_REGEX')

# Build regex if one is not defined in the settings file
if BASE_URL_REGEX is None:
    BASE_URL_REGEX = '^' + BASE_URL.lstrip('/')

DOCUMENTATION_URI = settings.get('DJANGO_SCIM_SP_DOC_URL')


