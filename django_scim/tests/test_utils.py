import json

from django.test import TestCase

from django_scim.utils import get_loggable_body


class LogCleanerTestCase(TestCase):

    def test_get_loggable_body(self):
        text = ('{"schemas":["urn:ietf:params:scim:api:messages:2.0:PatchOp"],'
                '"Operations":[{"op":"replace","value":{"password":"Lstar99&"}}]}')
        result = json.loads(get_loggable_body(text))
        expected = {
            "schemas":["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations":[{"op":"replace","value":{"password":"********"}}]
        }
        self.assertEqual(result, expected)


