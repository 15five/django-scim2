from django.test import TestCase
from django.test import Client

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class ViewTestCase(TestCase):
    def test_get_user_with_filter(self):
        c = Client()
        url = reverse('scim:user') + '?filter=userName eq ""'
        resp = c.get(url)

        self.assertEqual(resp.status_code, 200)

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

