"""
Transform filter query into QuerySet
"""
from django.contrib.auth import get_user_model

from scim2_filter_parser.query import Query

from . import exceptions
from .utils import get_group_model


class FilterQuery:
    model_getter = None
    joins = ()
    attr_map = None

    @classmethod
    def table_name(cls):
        return cls.model_getter()._meta.db_table

    @classmethod
    def search(cls, filter_query, request=None):
        q = Query(filter_query, cls.table_name(), cls.attr_map, cls.joins)
        return cls.model_getter().objects.raw(q.sql, q.params)


class UserFilterQuery(FilterQuery):
    model_getter = get_user_model
    attr_map = {}


class GroupFilterQuery(FilterQuery):
    model_getter = get_group_model
    attr_map = {}
