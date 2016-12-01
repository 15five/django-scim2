import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from django_scim.utils import get_user_adapter
from django_scim.utils import get_group_adapter


class SCIMUserTestCase(TestCase):
    def test_display_name(self):
        self.fail('TODO')

    def test_emails(self):
        self.fail('TODO')

    def test_groups(self):
        self.fail('TODO')

    def test_meta(self):
        self.fail('TODO')

    def test_to_dict(self):
        self.fail('TODO')

    def test_resource_type_dict(self):
        self.fail('TODO')



class SCIMGroupTestCase(TestCase):
    def test_display_name(self):
        self.fail('TODO')

    def test_members(self):
        self.fail('TODO')

    def test_meta(self):
        self.fail('TODO')

    def test_to_dict(self):
        self.fail('TODO')

    def test_resource_type_dict(self):
        self.fail('TODO')

