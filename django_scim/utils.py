from django.conf import settings
from django.utils.module_loading import import_string


DEFAULT_GROUP_MODEL_STRING = 'django.contrib.auth.models.Group'


def get_group_model():
    model_str = settings.get('DJANGO_SCIM_GROUP_MODEL', DEFAULT_GROUP_MODEL_STRING)
    return import_string(model_str)

