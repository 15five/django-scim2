from django.test import TestCase

from django_scim.grammars import USER_GRAMMAR
from django_scim.grammars import GROUP_GRAMMAR


class UserGrammarTestCase(TestCase):

    def test_parse_email(self):
        query = u'emails.value eq "ehughes@westworld.com"'
        USER_GRAMMAR.parse(query)

    def test_parse_username_with_slash(self):
        query = u'userName eq "ehughes@westworld.com/123"'
        USER_GRAMMAR.parse(query)


class GroupGrammarTestCase(TestCase):

    def test_parse_name(self):
        query = u'name eq "party-group"'
        GROUP_GRAMMAR.parse(query)

