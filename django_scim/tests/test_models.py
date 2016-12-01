import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from django_scim.utils import get_user_adapter
from django_scim.utils import get_group_adapter


class SCIMServiceProviderConfigTestCase(TestCase):
    def test_authentication_schemes(self):
        self.fail()

    def test_meta(self):
        self.fail()

    def test_location(self):
        self.fail()

    def test_to_dict(self):
        self.fail()

