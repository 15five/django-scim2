from django.conf import settings
from django.utils.module_loading import import_string

from .constants import DEFAULT_USER_ADAPTER_STRING
from .constants import DEFAULT_GROUP_MODEL_STRING
from .constants import DEFAULT_GROUP_ADAPTER_STRING


def get_user_adapter():
    model_str = getattr(settings, 'DJANGO_SCIM_USER_ADAPTER', DEFAULT_USER_ADAPTER_STRING)
    return import_string(model_str)


def get_group_model():
    model_str = getattr(settings, 'DJANGO_SCIM_GROUP_MODEL', DEFAULT_GROUP_MODEL_STRING)
    return import_string(model_str)


def get_group_adapter():
    model_str = getattr(settings, 'DJANGO_SCIM_GROUP_ADAPTER', DEFAULT_GROUP_ADAPTER_STRING)
    return import_string(model_str)


def get_base_scim_location_getter():
    """
    Return a function that will, when called, return the base
    location of scim app.
    """
    import_str = getattr(
        settings,
        'DJANGO_SCIM_BASE_LOCATION_GETTER',
        DEFAULT_BASE_LOCATION_GETTER_STRING
    )
    return import_string(import_str)


def default_base_scim_location_getter():
    base_scim_location_parts = (
        getattr(settings, 'DJANGO_SCIM_SCHEME', 'https'),
        settings.DJANGO_SCIM_NETLOC,
        '',  # path
        '',  # params
        '',  # query
        ''   # fragment
    )

    base_scim_location = moves.urllib.parse.urlunparse(base_scim_location_parts)

    return base_scim_location

