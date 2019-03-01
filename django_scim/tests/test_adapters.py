from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import connection
from django.db import models
from django.test import override_settings
from django.test import TestCase, RequestFactory

from django_scim import constants
from django_scim import models as scim_models
from django_scim.adapters import SCIMMixin
from django_scim.utils import get_group_adapter
from django_scim.utils import get_user_adapter


USER_MODEL = None
GROUP_MODEL = None


def setUpModule():
    global USER_MODEL
    global GROUP_MODEL

    # setup group
    class TestAdaptersGroup(scim_models.AbstractSCIMGroupMixin):
        name = models.CharField('name', max_length=80, unique=True)

    # setup user
    class TestAdaptersUser(scim_models.AbstractSCIMUserMixin, AbstractUser):
        scim_groups = models.ManyToManyField(
            TestAdaptersGroup,
            related_name="user_set",
        )

    USER_MODEL = TestAdaptersUser
    GROUP_MODEL = TestAdaptersGroup

    for model in (GROUP_MODEL, USER_MODEL):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)


def tearDownModule():
    for model in (GROUP_MODEL, USER_MODEL):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(model)


def get_group_model():
    return GROUP_MODEL


@override_settings(AUTH_USER_MODEL='django_scim.TestAdaptersUser')
class SCIMUserTestCase(TestCase):
    maxDiff = None
    request = RequestFactory().get('/fake/request')

    def test_display_name(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
        )
        ford = get_user_adapter()(ford, self.request)

        self.assertEqual(ford.display_name, 'Robert Ford')

    def test_emails(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        self.assertEqual(
            ford.emails,
            [{'primary': True, 'value': 'rford@ww.com'}]
        )

    def test_groups(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
        )
        ford.scim_groups.add(behavior)
        ford = get_user_adapter()(ford, self.request)

        expected = [
            {
                'display': u'Behavior Group',
                'value': '1',
                '$ref': u'https://localhost/scim/v2/Groups/1',
            }
        ]

        self.assertEqual(ford.groups, expected)

    def test_meta(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )

        expected = {
            'resourceType': 'User',
            'lastModified': ford.date_joined.isoformat(),
            'location': u'https://localhost/scim/v2/Users/1',
            'created': ford.date_joined.isoformat(),
        }

        ford = get_user_adapter()(ford, self.request)
        self.assertEqual(ford.meta, expected)

    def test_to_dict(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford.scim_groups.add(behavior)

        expected = {
            'schemas': [constants.SchemaURI.USER],
            'userName': 'rford',
            'meta': {
                'resourceType': 'User',
                'lastModified': ford.date_joined.isoformat(),
                'location': u'https://localhost/scim/v2/Users/1',
                'created': ford.date_joined.isoformat(),
            },
            'displayName': u'Robert Ford',
            'name': {
                'givenName': 'Robert',
                'familyName': 'Ford',
                'formatted': 'Robert Ford',
            },
            'groups': [
                {
                    'display': u'Behavior Group',
                    'value': '1',
                    '$ref': u'https://localhost/scim/v2/Groups/1'
                }
            ],
            'active': True,
            'id': '1',
            'emails': [{'primary': True, 'value': 'rford@ww.com'}],
        }

        ford = get_user_adapter()(ford, self.request)
        self.assertEqual(ford.to_dict(), expected)

    def test_resource_type_dict(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = {
            'endpoint': u'/scim/v2/Users',
            'description': 'User Account',
            'name': 'User',
            'meta': {
                'resourceType': 'ResourceType',
                'location': u'https://localhost/scim/v2/ResourceTypes/User'
            },
            'schemas': [constants.SchemaURI.RESOURCE_TYPE],
            'id': 'User',
            'schema': constants.SchemaURI.USER,
        }

        self.assertEqual(ford.resource_type_dict(), expected)


class SCIMMixinPathParserTestCase(TestCase):
    maxDiff = None

    def test_azure_ad_style_paths(self):
        """
        Test paths typically sent by AzureAD.
        """
        paths_and_values = [
            ("addresses[type eq \"work\"].country", 1),
            ("addresses[type eq \"work\"].locality", 1),
            ("addresses[type eq \"work\"].postalCode", 1),
            ("addresses[type eq \"work\"].streetAddress", 1),
            ("externalId", 1),
            ("urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department", 1),
        ]

        func = SCIMMixin(None).parse_path_and_value
        result_paths = list(map(lambda x: func(*x), paths_and_values))
        self.assertEqual(result_paths, paths_and_values)


@override_settings(AUTH_USER_MODEL='django_scim.TestAdaptersUser')
class SCIMGroupTestCase(TestCase):
    request = RequestFactory().get('/fake/request')

    def test_display_name(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        behavior = get_group_adapter()(behavior, self.request)
        self.assertEqual(behavior.display_name, 'Behavior Group')

    def test_members(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford.scim_groups.add(behavior)

        RequestFactory()
        behavior = get_group_adapter()(behavior, self.request)

        expected = [
            {
                'display': u'Robert Ford',
                'value': '1',
                '$ref': u'https://localhost/scim/v2/Users/1'
            }
        ]

        self.assertEqual(behavior.members, expected)

    def test_meta(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        behavior = get_group_adapter()(behavior, self.request)

        expected = {
            'resourceType': 'Group',
            'location': u'https://localhost/scim/v2/Groups/1'
        }

        self.assertEqual(behavior.meta, expected)

    def test_to_dict(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford.scim_groups.add(behavior)

        expected = {
            'meta': {
                'resourceType': 'Group',
                'location': u'https://localhost/scim/v2/Groups/1'
            },
            'displayName': 'Behavior Group',
            'id': '1',
            'members': [
                {
                    'display': u'Robert Ford',
                    'value': '1',
                    '$ref': u'https://localhost/scim/v2/Users/1'
                }
            ],
            'schemas': [constants.SchemaURI.GROUP]
        }

        behavior = get_group_adapter()(behavior, self.request)
        self.assertEqual(behavior.to_dict(), expected)

    def test_resource_type_dict(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        behavior = get_group_adapter()(behavior, self.request)

        expected = {
            'endpoint': u'/scim/v2/Groups',
            'description': 'Group',
            'name': 'Group',
            'meta': {
                'resourceType': 'ResourceType',
                'location': u'https://localhost/scim/v2/ResourceTypes/Group'
            },
            'schemas': [constants.SchemaURI.RESOURCE_TYPE],
            'id': 'Group',
            'schema': constants.SchemaURI.GROUP
        }

        self.assertEqual(behavior.resource_type_dict(), expected)

