"""
Filter transformers are used to convert the SCIM query and filter syntax into
valid SQL queries.
"""
import dateutil.parser
import itertools
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import plyplus

from . import exceptions
from .grammars import USER_GRAMMAR
from .grammars import GROUP_GRAMMAR
from .utils import get_group_model


STRING_REPLACEMENT_RE_PAT = re.compile(r'\%\([^).]+\)s', re.MULTILINE)


class QueryHelper:
    @classmethod
    def get_parsed_query(cls, query, request):
        try:
            return cls.grammar.parse(query)
        except plyplus.common.TokenizeError as e:
            error_string = str(e)
            if 'illegal character in input' in error_string.lower():
                raise exceptions.NotImplementedError(error_string)
            raise

    @classmethod
    def run_search_query(cls, parsed_query, request):
        try:
            sql, params = cls().transform(parsed_query)
            sql, params = cls.condition_sql_and_params(sql, params)
        except plyplus.PlyplusException as e:
            raise ValueError(e)
        else:
            return cls.model_cls_getter().objects.raw(sql, params)


class SCIMUserFilterTransformer(QueryHelper, plyplus.STransformer):
    """Transforms a PlyPlus parse tree into a tuple containing a raw SQL query
    and a dict with query parameters to go with the query."""

    grammar = USER_GRAMMAR
    model_cls_getter = get_user_model

    # data types:
    t_string = lambda self, exp: exp.tail[0][1:-1]  # noqa: 731
    t_date = lambda self, exp: dateutil.parser.parse(exp.tail[0][1:-1])  # noqa: 731
    t_bool = lambda self, exp: exp.tail[0] == u'true'  # noqa: 731

    # operators
    op_or = lambda self, exp: u'OR'  # noqa: 731
    op_and = lambda self, exp: u'AND'  # noqa: 731
    gt = ge = lt = le = pr = eq = co = sw = lambda self, ex: ex.tail[0].lower()  # noqa: 731

    # fully qualified column names:
    pk = lambda *args: u'u.id'  # noqa: 731
    username = lambda *args: u'u.username'  # noqa: 731
    external_id = lambda *args: u'u.external_id'  # noqa: 731
    password = lambda *args: u'u.password'  # noqa: 731
    first_name = lambda *args: u'u.first_name'  # noqa: 731
    last_name = lambda *args: u'u.last_name'  # noqa: 731
    email = lambda *args: u'u.email'  # noqa: 731
    date_joined = lambda *args: u'u.date_joined'  # noqa: 731
    is_active = lambda *args: u'u.is_active'  # noqa: 731

    @property
    def auth_user_db_table(self):
        return get_user_model()._meta.db_table

    # expressions:
    def logical_or(self, exp):
        # We're not doing a simple 'OR', as that doesn't scale when the two
        # conditions operate on different tables and rely on indices.
        # This is because Postgres' query planner cannot leverage indices from
        # different tables. Instead, we'll use a UNION.
        #
        # http://grokbase.com/t/postgresql/pgsql-general/034qrq6me0/left-join-not-using-index
        return u"""
            u.id IN (
                WITH users AS (
                    SELECT DISTINCT u.id
                    FROM {auth_user_db_table} u
                    {join}
                    WHERE
                    {operand1}

                    UNION

                    SELECT DISTINCT u.id
                    FROM {auth_user_db_table} u
                    {join}
                    WHERE
                    {operand2}
                )
                SELECT DISTINCT id FROM users
            )
        """.format(join=self.join(),
                   auth_user_db_table=self.auth_user_db_table,
                   operand1=exp.tail[0],
                   operand2=exp.tail[1])

    def logical_and(self, exp):
        op1, op2 = exp.tail
        if isinstance(op1, self.PasswordExpression):
            params = {'fragment': op2, 'password': op1}
        elif isinstance(op2, self.PasswordExpression):
            params = {'fragment': op1, 'password': op2}
        else:
            return u'(%s AND %s)' % (op1, op2)

        # When expensive CRYPT functions are involved we can't rely on
        # Postgres' query planner to chose the optimal order in which to
        # evaluate the conditions.
        # If a password condition is AND'ed against something else, we
        # explicitly write SQL that will force Postgres to compute the password
        # hashes on the *result* of the other condition, to minimize the number
        # of CRYPT calculations.
        return u"""
            u.id IN
            (
                WITH users AS (
                    SELECT DISTINCT u.id, u.password
                    FROM {auth_user_db_table} u
                    {join}
                    WHERE {fragment}
                )
                SELECT DISTINCT users.id
                FROM users
                WHERE {password}
            )""".format(join=self.join(),
                        auth_user_db_table=self.auth_user_db_table,
                        **params)

    __default__ = lambda self, exp: exp.tail[0]  # noqa: 731

    def __init__(self):
        self._seq = itertools.count(0, step=1)
        self._params = {}

    def _push_param(self, value):
        name = str(next(self._seq))
        self._params[name] = value
        return name

    def join(self):
        """Returns join expressions. E.g.

            JOIN bb_userprofile p ON p.user_id = u.id
        """
        return ''

    def start(self, exp):
        return u"""
            SELECT DISTINCT u.*
            FROM {auth_user_db_table} u
                {join}
            WHERE {fragment}
            ORDER BY u.id ASC
            """.format(join=self.join(),
                       auth_user_db_table=self.auth_user_db_table,
                       fragment=exp.tail[0]), self._params

    def un_expr(self, exp):
        return u'%s IS NOT NULL' % exp.tail[0]

    def un_string_expr(self, exp):
        # Django uses empty strings instead of NULL in VARCHARs:
        return u"(%s IS NOT NULL AND %s != '')" % (exp.tail[0], exp.tail[0])

    def bin_string_expr(self, exp):
        field, op, literal = exp.tail
        if op == u'eq':
            return u'UPPER(%s) = UPPER(%%(%s)s)' % (field, self._push_param(literal))
        elif op == u'sw':
            literal += u'%'
        elif op == u'co':
            literal = u'%' + literal + u'%'
        return u'%s ILIKE %%(%s)s' % (field, self._push_param(literal))

    def bin_date_expr(self, exp):
        field, op, literal = exp.tail
        op = {u'gt': u'>', u'ge': u'>=', u'lt': u'<', u'le': u'<='}[op]
        return u'%s %s %%(%s)s' % (field, op, self._push_param(literal))

    def bin_bool_expr(self, exp):
        return u'%s = %%(%s)s' % (exp.tail[0], self._push_param(exp.tail[2]))

    def bin_pk_expr(self, exp):
        field, op, value = exp.tail
        return u'%s = %%(%s)s' % (field, self._push_param(int(value)))

    def bin_passwd_expr(self, exp):
        pname = self._push_param(exp.tail[2])
        return self.PasswordExpression(u"""
            (
              CHAR_LENGTH(password) >= 51
              AND
              (
                -- Check for SHA1
                SPLIT_PART(password, '$', 3) = ENCODE(DIGEST(
                    SPLIT_PART(password, '$', 2')||%%(%s)s, 'sha1'), 'hex')
                OR
                -- Check for BCrypt
                SUBSTRING(password FROM 8) = CRYPT(
                  %%(%s)s, SUBSTRING(password FROM 8))
                OR
                -- Check for BCryptSHA256
                SUBSTRING(password FROM 15) = CRYPT(
                  ENCODE(DIGEST(%%(%s)s, 'sha256'), 'hex'),
                  SUBSTRING(password FROM 15))
              )
            )""" % (pname, pname, pname))

    @classmethod
    def condition_sql_and_params(cls, sql, params):
        # replace %(id)s with %s and update params accordingly
        replacements = STRING_REPLACEMENT_RE_PAT.findall(sql)
        new_sql = STRING_REPLACEMENT_RE_PAT.sub('%s', sql, count=len(replacements))

        new_params = []
        for replacement in replacements:
            # strip '%(' adn ')s' from replacement arg
            replacement = replacement[2:-2]
            new_params.append(params.get(replacement))

        return new_sql, new_params

    @classmethod
    def search(cls, query, request=None):
        """Takes a SCIM 1.1 filter query and returns a Django `QuerySet` that
        contains zero or more user model instances.

        :param unicode query: a `unicode` query string.
        """
        parsed_query = cls.get_parsed_query(query, request)
        return cls.run_search_query(parsed_query, request)

    class PasswordExpression(object):
        def __init__(self, sql):
            assert isinstance(sql, str)
            self.sql = sql

        def __str__(self):
            return self.sql.encode('utf-8')

        def __unicode__(self):
            return self.sql


class SCIMGroupFilterTransformer(QueryHelper, plyplus.STransformer):
    """Transforms a PlyPlus parse tree into a tuple containing a raw SQL query
    and a dict with query parameters to go with the query."""

    grammar = GROUP_GRAMMAR
    model_cls_getter = get_group_model

    # data types:
    t_string = lambda self, exp: exp.tail[0][1:-1]  # noqa: 731

    # operators
    op_or = lambda self, exp: u'OR'  # noqa: 731
    op_and = lambda self, exp: u'AND'  # noqa: 731
    pr = eq = co = sw = lambda self, ex: ex.tail[0].lower()  # noqa: 731

    # fully qualified column names:
    pk = lambda *args: u'g.id'  # noqa: 731
    name = lambda *args: u'g.name'  # noqa: 731

    @property
    def group_table(self):
        return Group._meta.db_table

    # expressions:
    def logical_or(self, exp):
        # We're not doing a simple 'OR', as that doesn't scale when the two
        # conditions operate on different tables and rely on indices.
        # This is because Postgres' query planner cannot leverage indices from
        # different tables. Instead, we'll use a UNION.
        #
        # http://grokbase.com/t/postgresql/pgsql-general/034qrq6me0/left-join-not-using-index
        return u"""
            g.id IN (
                WITH group AS (
                    SELECT DISTINCT g.id
                    FROM {group_table} g
                    {join}
                    WHERE
                    {operand1}

                    UNION

                    SELECT DISTINCT g.id
                    FROM {group_table} g
                    {join}
                    WHERE
                    {operand2}
                )
                SELECT DISTINCT id FROM groups
            )
        """.format(join=self.join(),
                   group_table=self.group_table,
                   operand1=exp.tail[0],
                   operand2=exp.tail[1])

    def logical_and(self, exp):
        op1, op2 = exp.tail
        return u'(%s AND %s)' % (op1, op2)

    __default__ = lambda self, exp: exp.tail[0]  # noqa: 731

    def __init__(self):
        self._seq = itertools.count(0, step=1)
        self._params = {}

    def _push_param(self, value):
        name = str(next(self._seq))
        self._params[name] = value
        return name

    def join(self):
        """Returns join expressions. E.g.

            JOIN bb_userprofile p ON p.user_id = u.id
        """
        return ''

    def start(self, exp):
        return u"""
            SELECT DISTINCT g.*
            FROM {group_table} g
                {join}
            WHERE {fragment}
            ORDER BY g.id ASC
            """.format(join=self.join(),
                       group_table=self.group_table,
                       fragment=exp.tail[0]), self._params

    def un_string_expr(self, exp):
        # Django uses empty strings instead of NULL in VARCHARs:
        return u"(%s IS NOT NULL AND %s != '')" % (exp.tail[0], exp.tail[0])

    def bin_string_expr(self, exp):
        field, op, literal = exp.tail
        if op == u'eq':
            return u'UPPER(%s) = UPPER(%%(%s)s)' % (field, self._push_param(literal))
        elif op == u'sw':
            literal += u'%'
        elif op == u'co':
            literal = u'%' + literal + u'%'
        return u'%s ILIKE %%(%s)s' % (field, self._push_param(literal))

    def bin_pk_expr(self, exp):
        field, op, value = exp.tail
        return u'%s = %%(%s)s' % (field, self._push_param(int(value)))

    @classmethod
    def condition_sql_and_params(cls, sql, params):
        # replace %(id)s with %s and update params accordingly
        replacements = STRING_REPLACEMENT_RE_PAT.findall(sql)
        new_sql = STRING_REPLACEMENT_RE_PAT.sub('%s', sql, count=len(replacements))

        new_params = []
        for replacement in replacements:
            # strip '%(' adn ')s' from replacement arg
            replacement = replacement[2:-2]
            new_params.append(params.get(replacement))

        return new_sql, new_params

    @classmethod
    def search(cls, query, request=None):
        """Takes a SCIM 1.1 filter query and returns a Django `QuerySet` that
        contains zero or more group model instances.

        :param unicode query: a `unicode` query string.
        """
        parsed_query = cls.get_parsed_query(query, request)
        return cls.run_search_query(parsed_query, request)
