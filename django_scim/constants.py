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

