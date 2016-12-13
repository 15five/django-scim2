import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from django_scim.utils import get_user_adapter
from django_scim.utils import get_group_adapter
from django_scim.utils import get_group_model


class SCIMUserTestCase(TestCase):
    maxDiff = None

    def test_display_name(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
        )
        ford = get_user_adapter()(ford)

        self.assertEqual(ford.display_name, 'Robert Ford')

    def test_emails(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford)

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
        ford.groups.add(behavior)
        ford = get_user_adapter()(ford)

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

        ford = get_user_adapter()(ford)
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
        ford.groups.add(behavior)

        expected = {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
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

        ford = get_user_adapter()(ford)
        self.assertEqual(ford.to_dict(), expected)

    def test_resource_type_dict(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )
        ford = get_user_adapter()(ford)

        expected = {
            'endpoint': u'/scim/v2/Users',
            'description': 'User Account',
            'name': 'User',
            'meta': {
                'resourceType': 'ResourceType',
                'location': u'https://localhost/scim/v2/ResourceTypes/User'
            },
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ResourceType'],
            'id': 'User',
            'schema': 'urn:ietf:params:scim:schemas:core:2.0:User'
        }

        self.assertEqual(ford.resource_type_dict(), expected)


class SCIMGroupTestCase(TestCase):
    def test_display_name(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        behavior = get_group_adapter()(behavior)
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
        ford.groups.add(behavior)

        behavior = get_group_adapter()(behavior)

        expected =  [
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
        behavior = get_group_adapter()(behavior)

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
        ford.groups.add(behavior)

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
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:Group']
        }

        behavior = get_group_adapter()(behavior)
        self.assertEqual(behavior.to_dict(), expected)

    def test_resource_type_dict(self):
        behavior = get_group_model().objects.create(
            name='Behavior Group',
        )
        behavior = get_group_adapter()(behavior)

        expected = {
            'endpoint': u'/scim/v2/Groups',
            'description': 'Group',
            'name': 'Group',
            'meta': {
                'resourceType': 'ResourceType',
                'location': u'https://localhost/scim/v2/ResourceTypes/Group'
            },
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ResourceType'],
            'id': 'Group',
            'schema': 'urn:ietf:params:scim:schemas:core:2.0:Group'
        }

        self.assertEqual(behavior.resource_type_dict(), expected)

