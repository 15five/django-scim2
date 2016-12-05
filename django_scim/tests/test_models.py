import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from django_scim.utils import get_user_adapter
from django_scim.utils import get_group_adapter

from django_scim.models import SCIMServiceProviderConfig


class SCIMServiceProviderConfigTestCase(TestCase):
    maxDiff = None

    def test_authentication_schemes(self):
        config = SCIMServiceProviderConfig()
        self.assertEqual(config.authentication_schemes, [])

    def test_meta(self):
        config = SCIMServiceProviderConfig()
        expected = {
            'resourceType': 'ServiceProviderConfig',
            'location': u'https://localhost/scim/v2/ServiceProviderConfig',
        }
        self.assertEqual(config.meta, expected)

    def test_location(self):
        config = SCIMServiceProviderConfig()
        location = 'https://localhost/scim/v2/ServiceProviderConfig'
        self.assertEqual(config.location, location)

    def test_to_dict(self):
        config = SCIMServiceProviderConfig()
        expected ={
            'authenticationSchemes': [],
            'bulk': {'supported': False},
            'changePassword': {'supported': True},
            'documentationUri': None,
            'etag': {'supported': False},
            'filter': {'supported': True},
            'meta': {
                'location': u'https://localhost/scim/v2/ServiceProviderConfig',
                'resourceType': 'ServiceProviderConfig'
            },
            'patch': {'supported': True},
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig'],
            'sort': {'supported': False}
        }
        self.assertEqual(config.to_dict(), expected)

