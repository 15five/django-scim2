import dateutil.parser
import itertools

from plyplus import Grammar, STransformer, PlyplusException
from django.contrib.auth.models import User


grammar = Grammar("""
  start: logical_or;

  ?logical_or: logical_or 'or' logical_and | logical_and;
  ?logical_and: logical_and 'and' expr | expr;

  ?expr: (un_string_expr | un_expr) | bin_expr | '\(' logical_or '\)';

  ?bin_expr: (bin_string_expr | bin_passwd_expr | bin_pk_expr | bin_date_expr |
              bin_bool_expr);

  un_string_expr: (string_field | password) pr;
  un_expr: (date_field | bool_field) pr;
  bin_string_expr: string_field string_op t_string;
  bin_passwd_expr: password eq t_string;
  bin_pk_expr: pk eq t_string;
  bin_date_expr: date_field date_op t_date;
  bin_bool_expr: bool_field eq t_bool;

  ?string_op: eq | co | sw;
  ?date_op: eq | gt | ge | lt | le;

  pr: '(?i)pr';
  eq: '(?i)eq';
  co: '(?i)co';
  sw: '(?i)sw';
  pr: '(?i)pr';
  gt: '(?i)gt';
  ge: '(?i)ge';
  lt: '(?i)lt';
  le: '(?i)le';

  ?string_field: username | first_name | last_name | email;
  ?date_field: date_joined;
  ?bool_field: is_active;

  username: '(?i)userName';
  first_name: '(?i)name\.givenName' | '(?i)givenName';
  last_name: '(?i)name\.familyName' | '(?i)familyName';
  password: '(?i)password';
  pk: '(?i)id';
  date_joined: '(?i)meta\.created' | '(?i)created';
  email: '(?i)emails\.value' | '(?i)emails';
  is_active: '(?i)active';

  t_string: '"(?:[^"\\\\]|\\\\.)*"' ;
  t_date: '"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[Zz]?"';
  t_bool: 'false' | 'true';

  SPACES: '[ ]+' (%ignore);
  """)


class SCIMFilterTransformer(STransformer):
    """Transforms a PlyPlus parse tree into a tuple containing a raw SQL query
    and a dict with query parameters to go with the query."""

    # data types:
    t_string = lambda self, exp: exp.tail[0][1:-1]
    t_date = lambda self, exp: dateutil.parser.parse(exp.tail[0][1:-1])
    t_bool = lambda self, exp: exp.tail[0] == 'true'

    # fully qualified column names:
    pk = lambda *args: 'u.id'
    username = lambda *args: 'u.username'
    password = lambda *args: 'u.password'
    first_name = lambda *args: 'u.first_name'
    last_name = lambda *args: 'u.last_name'
    email = lambda *args: 'u.email'
    date_joined = lambda *args: 'u.date_joined'
    is_active = lambda *args: 'u.is_active'

    # expressions:
    logical_or = lambda self, exp: '(%s OR %s)' % (exp.tail[0], exp.tail[1])
    logical_and = lambda self, exp: '(%s AND %s)' % (exp.tail[0], exp.tail[1])

    # operators:
    gt = ge = lt = le = pr = eq = co = sw = lambda self, ex: ex.tail[0].lower()

    __default__ = lambda self, exp: exp.tail[0]

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
        return """
            SELECT DISTINCT u.*
            FROM auth_user u
                {joins}
            WHERE {fragment}
            ORDER BY u.id ASC
            """.format(joins=self.join(), fragment=exp.tail[0]), self._params

    def un_expr(self, exp):
        return '%s IS NOT NULL' % exp.tail[0]

    def un_string_expr(selfself, exp):
        # Django uses empty strings instead of NULL in VARCHARs:
        return "(%s IS NOT NULL AND %s != '')" % (exp.tail[0], exp.tail[0])

    def bin_string_expr(self, exp):
        field, op, literal = exp.tail
        if op == 'sw':
            literal += '%'
        elif op == 'co':
            literal = '%' + literal + '%'
        return '%s ILIKE %%(%s)s' % (field, self._push_param(literal))

    def bin_date_expr(self, exp):
        field, op, literal = exp.tail
        return '%s %s %%(%s)s' % (
            field, {'gt': '>', 'ge': '>=', 'lt': '<', 'le': '<='}[op],
            self._push_param(literal))

    def bin_bool_expr(self, exp):
        return '%s = %%(%s)s' % (exp.tail[0], self._push_param(exp.tail[2]))

    def bin_pk_expr(self, exp):
        field, op, value = exp.tail
        return '%s = %%(%s)s' % (field, self._push_param(int(value)))

    def bin_passwd_expr(self, exp):
        pname = self._push_param(exp.tail[2])
        return """
            (
              CHAR_LENGTH(password) >= 51
              AND
              (
                -- Check for SHA1
                SUBSTRING(password FROM 12) = ENCODE(DIGEST(SUBSTRING(
                    password FROM 6 FOR 5)||%%(%s)s, 'sha1'), 'hex')
                OR
                -- Check for BCrypt
                SUBSTRING(password FROM 8) = CRYPT(
                  %%(%s)s, SUBSTRING(password FROM 8))
              )
            )""" % (pname, pname)

    @classmethod
    def search(cls, query):
        """Takes a SCIM 1.1 filter query and returns a Django `QuerySet` that
        contains zero or more `User` instances.

        :param unicode query:   a `unicode` query string.
        """
        try:
            sql, params = cls().transform(grammar.parse(query))
        except PlyplusException, e:
            raise ValueError(e)
        else:
            return User.objects.raw(sql, params)
