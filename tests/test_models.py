import django
from django.test import TestCase, override_settings

from django_scim import constants
from django_scim.utils import get_service_provider_config_model, get_user_model

# Force loading of test.models so its models are registered with Django and
# testing framework.
from tests.models import get_group_model as _unused


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
        expected = {
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
                'supported': False,
                'maxResults': 50
            },
            'meta': {
                'location': u'https://localhost/scim/v2/ServiceProviderConfig',
                'resourceType': 'ServiceProviderConfig'
            },
            'patch': {'supported': True},
            'schemas': [constants.SchemaURI.SERVICE_PROVIDER_CONFIG],
            'sort': {'supported': False}
        }
        self.assertEqual(config.to_dict(), expected)


@override_settings(AUTH_USER_MODEL='django_scim.TestUser')
class UserTestCase(TestCase):
    maxDiff = None

    def test_get_user_by_id_duplicate_none_scim_id(self):
        """
        Test GET /Users/{id}
        """
        # create user
        ford = get_user_model().objects.create(
            username='robert.ford',
            first_name='Robert',
            last_name='Ford',
        )
        ford.scim_id = None
        ford.save()

        # create user with duplicate scim_id that is None
        ford2 = get_user_model().objects.create(
            username='robert2.ford2',
            first_name='Robert2',
            last_name='Ford2',
        )
        ford2.scim_id = None
        ford2.save()

    def test_get_user_by_id_duplicate_value_scim_id(self):
        """
        Test GET /Users/{id}
        """
        # create user
        ford = get_user_model().objects.create(
            username='robert.ford',
            first_name='Robert',
            last_name='Ford',
        )
        scim_id = ford.scim_id

        # create user with duplicate scim_id
        ford2 = get_user_model().objects.create(
            username='robert2.ford2',
            first_name='Robert2',
            last_name='Ford2',
        )
        ford2.scim_id = scim_id

        with self.assertRaises(django.db.utils.IntegrityError):
            ford2.save()
