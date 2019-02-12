import unittest

from django.test import TestCase

from django_scim.grammars import USER_GRAMMAR
from django_scim.grammars import GROUP_GRAMMAR


class UserGrammarTestCase(TestCase):

    def test_parse_email(self):
        query = u'emails.value eq "ehughes@westworld.com"'
        USER_GRAMMAR.parse(query)

    def test_parse_username(self):
        query = u'userName eq "ehughes@westworld.com"'
        USER_GRAMMAR.parse(query)

    def test_parse_username_with_slash(self):
        query = u'userName eq "ehughes@westworld.com/123"'
        USER_GRAMMAR.parse(query)

    @unittest.skip('One day...')
    def test_azure_ad_style_email_filter_query(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        USER_GRAMMAR.parse(query)


class GroupGrammarTestCase(TestCase):

    def test_parse_name(self):
        query = u'name eq "Security-Team"'
        GROUP_GRAMMAR.parse(query)

    def test_parse_name(self):
        query = u'displayName eq "Security-Team"'
        GROUP_GRAMMAR.parse(query)
