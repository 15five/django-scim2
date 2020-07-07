from django.contrib.auth import get_user_model

from django_scim.filters import FilterQuery
from django_scim.utils import get_group_model


class UserFilterQuery(FilterQuery):
    model_getter = get_user_model
    attr_map = {
        ('userName', None, None): 'username',
        ('name', 'familyName', None): 'last_name',
        ('familyName', None, None): 'last_name',
        ('name', 'givenName', None): 'first_name',
        ('givenName', None, None): 'first_name',
        ('active', None, None): 'is_active',
    }


class GroupFilterQuery(FilterQuery):
    model_getter = get_group_model
    attr_map = {}
