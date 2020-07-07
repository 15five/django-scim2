from django.contrib.auth import get_user_model
from django.test import TestCase

from tests.filters import UserFilterQuery


class Users(TestCase):
    parser = UserFilterQuery

    def setUp(self):
        self.ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        self.abernathy = get_user_model().objects.create(
            first_name='Dolores',
            last_name='Abernathy',
            username='dabernathy',
        )

    def test_username_eq(self):
        query = 'userName eq "rford"'
        qs = list(self.parser.search(query))
        expected = [self.ford]
        self.assertEqual(qs, expected)
