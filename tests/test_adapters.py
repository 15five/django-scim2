from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings
from scim2_filter_parser.attr_paths import AttrPath

from django_scim import constants
from django_scim.adapters import SCIMMixin
from django_scim.utils import get_group_adapter, get_user_adapter, get_user_model

from tests.models import get_group_model


@override_settings(AUTH_USER_MODEL='django_scim.TestUser')
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
            scim_external_id='Anthony.Hopkins',
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
            'externalId': 'Anthony.Hopkins',
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


@override_settings(AUTH_USER_MODEL='django_scim.TestUser')
class SCIMHandleOperationsTestCase(TestCase):
    maxDiff = None
    request = RequestFactory().get('/fake/request')

    def test_handle_replace_simple(self):
        operations = [
            {
                "op": "Replace",
                "path": "externalId",
                "value": "Robert.Ford"
            },
        ]

        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = (
            ('externalId', None, None),
            'Robert.Ford',
            operations[0]
        )

        with patch('django_scim.adapters.SCIMUser.handle_replace') as handler:
            ford.handle_operations(operations)
            call_args = handler.call_args[0]
            self.assertIsInstance(call_args[0], AttrPath)
            self.assertEqual(call_args[0].first_path, expected[0])
            self.assertEqual(call_args[1], expected[1])
            self.assertEqual(call_args[2], expected[2])

    def test_handle_replace_complex(self):
        operations = [
            {
                "op": "Replace",
                "path": "name.givenName",
                "value": "Robert"
            },
        ]

        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = (
            ('name', 'givenName', None),
            'Robert',
            operations[0]
        )

        with patch('django_scim.adapters.SCIMUser.handle_replace') as handler:
            ford.handle_operations(operations)
            call_args = handler.call_args[0]
            self.assertIsInstance(call_args[0], AttrPath)
            self.assertEqual(call_args[0].first_path, expected[0])
            self.assertEqual(call_args[1], expected[1])
            self.assertEqual(call_args[2], expected[2])

    def test_handle_add_simple(self):
        operations = [
            {
                "op": "Add",
                "path": "externalId",
                "value": "Robert.Ford"
            },
        ]

        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = (
            ('externalId', None, None),
            'Robert.Ford',
            operations[0]
        )

        with patch('django_scim.adapters.SCIMUser.handle_add') as handler:
            ford.handle_operations(operations)
            call_args = handler.call_args[0]
            self.assertIsInstance(call_args[0], AttrPath)
            self.assertEqual(call_args[0].first_path, expected[0])
            self.assertEqual(call_args[1], expected[1])
            self.assertEqual(call_args[2], expected[2])

    def test_handle_add_complex_1(self):
        operations = [
            {
                "op": "Add",
                "path": "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department",
                "value": "Design"
            }
        ]

        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = (
            ('department', None, 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'),
            'Design',
            operations[0]
        )

        with patch('django_scim.adapters.SCIMUser.handle_add') as handler:
            ford.handle_operations(operations)

            call_args = handler.call_args[0]
            self.assertIsInstance(call_args[0], AttrPath)
            self.assertEqual(call_args[0].first_path, expected[0])
            self.assertEqual(call_args[1], expected[1])
            self.assertEqual(call_args[2], expected[2])

    def test_handle_add_complex_2(self):
        operations = [
            {
                "op": "Add",
                "path": "addresses[type eq \"work\"].country",
                "value": "Sector 9"
            }
        ]

        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = (
            ('addresses', 'country', None),
            'Sector 9',
            operations[0]
        )

        with patch('django_scim.adapters.SCIMUser.handle_add') as handler:
            ford.handle_operations(operations)
            path_obj, value, op_dict = handler.call_args[0]
            self.assertEqual(path_obj.filter, 'addresses[type eq \"work\"].country eq ""')
            self.assertEqual(
                list(path_obj),
                [('addresses', 'type', None), ('addresses', 'country', None)]
            )
            self.assertEqual(value, 'Sector 9')
            self.assertEqual(op_dict, operations[0])

    def test_handle_add_complex_3(self):
        operations = [
            {
                "op": "Add",
                "path": 'members[value eq "6784"]',
                "value": "[]"
            }
        ]

        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford, self.request)

        expected = (
            ('addresses', 'country', None),
            'Sector 9',
            operations[0]
        )

        with patch('django_scim.adapters.SCIMUser.handle_add') as handler:
            ford.handle_operations(operations)
            path_obj, value, op_dict = handler.call_args[0]
            self.assertEqual(path_obj.filter, 'members[value eq "6784"] eq ""')
            self.assertEqual(
                list(path_obj),
                [('members', 'value', None), ('members', None, None)]
            )
            self.assertEqual(value, '[]')
            self.assertEqual(op_dict, operations[0])


class SCIMMixinPathParserTestCase(TestCase):
    maxDiff = None

    def test_azure_ad_style_paths(self):
        """
        Test paths typically sent by AzureAD.
        """
        paths_and_values = [
            ('addresses[type eq \"work\"].country', 1),
            ('addresses[type eq \"work\"].locality', 1),
            ('addresses[type eq \"work\"].postalCode', 1),
            ('addresses[type eq \"work\"].streetAddress', 1),
        ]

        expected_paths_and_values = [
            {
                'path': 'addresses[type eq \"work\"].country eq ""',
                'attr_paths': [('addresses', 'type', None), ('addresses', 'country', None)]
            },
            {
                'path': 'addresses[type eq \"work\"].locality eq ""',
                'attr_paths': [('addresses', 'type', None), ('addresses', 'locality', None)]
            },
            {
                'path': 'addresses[type eq \"work\"].postalCode eq ""',
                'attr_paths': [('addresses', 'type', None), ('addresses', 'postalCode', None)]
            },
            {
                'path': 'addresses[type eq \"work\"].streetAddress eq ""',
                'attr_paths': [('addresses', 'type', None), ('addresses', 'streetAddress', None)]
            }
        ]


        func = SCIMMixin(None).parse_path_and_values
        result_paths = list(map(lambda x: func(*x), paths_and_values))
        for paths_and_values, expected in zip(result_paths, expected_paths_and_values):
            path_obj, _ = paths_and_values[0]
            self.assertEqual(path_obj.filter, expected['path'])
            self.assertEqual(list(path_obj), expected['attr_paths'])

    def test_correct_path_tuples(self):
        """
        Test paths regex
        """
        paths_and_expected_values = [
            (
                'externalId',
                ('externalId', None, None),
            ),
            (
                'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department',
                ('department', None, 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'),
            ),
            (
                'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:name.familyName',
                ('name', 'familyName', 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'),
            ),
        ]

        func = SCIMMixin(None).parse_path_and_values
        for path, expected_result in paths_and_expected_values:
            result, _ = func(path, None)[0]
            self.assertEqual(result.first_path, expected_result)


@override_settings(AUTH_USER_MODEL='django_scim.TestUser')
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
            scim_external_id='ww.bg',
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
            'schemas': [constants.SchemaURI.GROUP],
            'externalId': 'ww.bg',
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
