from django.test import TestCase

from django_scim.filters import user_grammar


class UserGrammarTestCase(TestCase):

    def test_user_grammar_parse_email(self):
        query = u'emails.value eq "ehughes@westworld.com"'
        user_grammar.parse(query)

    def test_user_grammar_parse_username_with_slash(self):
        query = u'userName eq "ehughes@westworld.com/123"'
        user_grammar.parse(query)
