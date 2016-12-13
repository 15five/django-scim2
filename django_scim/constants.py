from django.conf import settings
from django.utils.six import moves


DJANGO_SCIM_BASE_LOCATION_GETTER = 'django_scim.utils.default_base_scim_location_getter'

DEFAULT_USER_ADAPTER_STRING = 'django_scim.adapters.SCIMUser'

DEFAULT_GROUP_MODEL_STRING = 'django.contrib.auth.models.Group'
DEFAULT_GROUP_ADAPTER_STRING = 'django_scim.adapters.SCIMGroup'

DOCUMENTATION_URI = getattr(settings, 'DJANGO_SCIM_SP_DOC_URL', None)

SCHEMA_URI_ERROR = 'urn:ietf:params:scim:api:messages:2.0:Error'

