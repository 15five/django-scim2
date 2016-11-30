import json

from django.test import TestCase
from django.test import Client

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class ViewTestCase(TestCase):
    def test_get_user_with_username_filter(self):
        c = Client()
        url = reverse('scim:users-search')
        body = json.dumps({'filter': 'userName eq ""'})
        resp = c.post(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

#Get User with userName filter
#
#Create User
#
#Get User by ID
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

