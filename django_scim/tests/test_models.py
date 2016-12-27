import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from django_scim.utils import get_user_adapter
from django_scim.utils import get_group_adapter
from django_scim.utils import get_service_provider_config_model


class SCIMServiceProviderConfigTestCase(TestCase):
    maxDiff = None

    def test_meta(self):
        config = get_service_provider_config_model()()
        expected = {
            'resourceType': 'ServiceProviderConfig',
            'location': u'https://localhost/scim/v2/ServiceProviderConfig',
        }
        self.assertEqual(config.meta, expected)

    def test_location(self):
        config = get_service_provider_config_model()()
        location = 'https://localhost/scim/v2/ServiceProviderConfig'
        self.assertEqual(config.location, location)

    def test_to_dict(self):
        config = get_service_provider_config_model()()
        expected ={
            'authenticationSchemes': [
                {
                    'description': 'Oauth 2 implemented with bearer token',
                    'documentationUri': '',
                    'name': 'OAuth 2',
                    'specUri': '',
                    'type': 'oauth2'
                }
            ],
            'bulk': {
                'supported': False,
                'maxPayloadSize': 1048576,
                'maxOperations': 1000,
            },
            'changePassword': {'supported': True},
            'documentationUri': None,
            'etag': {'supported': False},
            'filter': {
                'supported': True,
                'maxResults': 50
            },
            'meta': {
                'location': u'https://localhost/scim/v2/ServiceProviderConfig',
                'resourceType': 'ServiceProviderConfig'
            },
            'patch': {'supported': True},
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig'],
            'sort': {'supported': False}
        }
        self.assertEqual(config.to_dict(), expected)

