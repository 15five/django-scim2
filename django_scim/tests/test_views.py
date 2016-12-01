import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from django_scim.utils import get_user_adapter


class ViewTestCase(TestCase):
    maxDiff = None

    def test_search_without_schema(self):
        """
        Test POST /Users/.search/?filter=userName eq ""
        """
        c = Client()
        url = reverse('scim:users-search')
        body = json.dumps({
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:NotSearchRequest'],
        })
        resp = c.post(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 400, resp.content)

        result = json.loads(resp.content)
        expected = {
            "Errors": [
                {
                    "code": 400,
                    "description": "Invalid schema uri. Must be SearchRequest."
                }
            ]
        }
        self.assertEqual(expected, result)

    def test_search_for_user_with_username_filter(self):
        """
        Test POST /Users/.search/?filter=userName eq ""
        """
        c = Client()
        url = reverse('scim:users-search')
        body = json.dumps({
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:SearchRequest'],
            'filter': 'userName eq ""',
        })
        resp = c.post(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 0,
            "itemsPerPage": 50,
            "startIndex": 1,
            "Resources": [],
        }
        self.assertEqual(expected, result)

    def test_get_user_with_username_filter(self):
        """
        Test GET /Users?filter=userName eq ""
        """
        c = Client()
        url = reverse('scim:users') + '?filter=userName eq ""'
        resp = c.get(url, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 0,
            "itemsPerPage": 50,
            "startIndex": 1,
            "Resources": [],
        }
        self.assertEqual(expected, result)

    def test_get_user_by_id(self):
        """
        Test GET /Users/{id}
        """
        # create user
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford'
        )
        ford = get_user_adapter()(ford)

        c = Client()
        url = reverse('scim:users', kwargs={'uuid': ford.id})
        resp = c.get(url, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        result = json.loads(resp.content)
        expected = ford.to_dict()
        self.assertEqual(expected, result)

    def test_get_all_users(self):
        """
        Test GET /Users
        """
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
        )
        ford = get_user_adapter()(ford)
        abernathy = get_user_model().objects.create(
            first_name='Dolores',
            last_name='Abernathy',
            username='dabernathy',
        )
        abernathy = get_user_adapter()(abernathy)

        c = Client()
        url = reverse('scim:users')
        resp = c.get(url, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 2,
            "itemsPerPage": 50,
            "startIndex": 1,
            'Resources': [
                ford.to_dict(),
                abernathy.to_dict(),
            ],
        }
        self.assertEqual(expected, result)


#Create User
#
#
#Update User
#
#Get Groups
#
#Create Group
#
#Patch Group 
#
#Delete User
#
#Get Users

