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

