"""
Transform filter query into QuerySet
"""
from django.contrib.auth import get_user_model

from scim2_filter_parser.query import Query

from . import exceptions
from .utils import get_group_model


class FilterQuery:
    model = None
    joins = ()
    attr_map = None

    @classmethod
    def search(cls, filter_query):
        table_name = cls.model._meta.db_table
        q = Query(filter_query, table_name, cls.attr_map, cls.joins)
        return cls.model.objects.raw(q.sql, q.params)


class UserFilterQuery(FilterQuery):
    model = get_user_model()
    attr_map = {}


class GroupFilterQuery(FilterQuery):
    model = get_group_model()
    attr_map = {}

