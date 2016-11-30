from django.conf import settings
from django.utils.module_loading import import_string

from .constants import DEFAULT_GROUP_MODEL_STRING


def get_group_model():
    model_str = getattr(settings, 'DJANGO_SCIM_GROUP_MODEL', DEFAULT_GROUP_MODEL_STRING)
    return import_string(model_str)

