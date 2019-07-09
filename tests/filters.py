from django.contrib.auth import get_user_model

from django_scim.filters import FilterQuery
from django_scim.utils import get_group_model


class UserFilterQuery(FilterQuery):
    model_getter = get_user_model
    attr_map = {
        ('userName', None, None): 'username',
    }


class GroupFilterQuery(FilterQuery):
    model_getter = get_group_model
    attr_map = {}

