import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import connection, models
from django.test import TestCase, override_settings

from django_scim import constants
from django_scim import models as scim_models
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


USER_MODEL = None
GROUP_MODEL = None


def setUpModule():
    global USER_MODEL
    global GROUP_MODEL

    # setup group
    class TestModelsGroup(scim_models.AbstractSCIMGroupMixin):
        name = models.CharField('name', max_length=80, unique=True)

        class Meta:
            app_label = 'django_scim'

    # setup user
    class TestModelsUser(scim_models.AbstractSCIMUserMixin, AbstractUser):
        scim_groups = models.ManyToManyField(
            TestModelsGroup,
            related_name="user_set",
        )

        class Meta:
            app_label = 'django_scim'

    USER_MODEL = TestModelsUser
    GROUP_MODEL = TestModelsGroup

    for model in (GROUP_MODEL, USER_MODEL):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)


def tearDownModule():
    for model in (GROUP_MODEL, USER_MODEL):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(model)


def get_group_model():
    return GROUP_MODEL


@override_settings(AUTH_USER_MODEL='django_scim.TestModelsUser')
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
