from django.conf import settings
from django.utils.six import moves


BASE_SCIM_LOCATION_PARTS = (
    getattr(settings, 'DJANGO_SCIM_SCHEME', 'https'),
    settings.DJANGO_SCIM_NETLOC,
    '',  # path
    '',  # params
    '',  # query
    ''   # fragment
)

BASE_SCIM_LOCATION = moves.urllib.parse.urlunparse(BASE_SCIM_LOCATION_PARTS)

DEFAULT_USER_ADAPTER_STRING = 'django_scim.adapters.SCIMUser'

DEFAULT_GROUP_MODEL_STRING = 'django.contrib.auth.models.Group'
DEFAULT_GROUP_ADAPTER_STRING = 'django_scim.adapters.SCIMGroup'

DOCUMENTATION_URI = getattr(settings, 'DJANGO_SCIM_SP_DOC_URL', None)

SCHEMA_URI_ERROR = 'urn:ietf:params:scim:api:messages:2.0:Error'

