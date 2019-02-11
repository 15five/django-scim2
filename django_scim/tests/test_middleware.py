from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from django_scim.middleware import SCIMAuthCheckMiddleware


class SCIMMiddlewareTestCase(TestCase):
    def test_middleware_for_django2(self):
        """
        Regression test for https://github.com/15five/django-scim2/issues/13
        """
        check = SCIMAuthCheckMiddleware()

        request = RequestFactory().get(check.reverse_url)
        request.user = AnonymousUser()

        response = check.process_request(request)
        self.assertEqual(response.status_code, 401)

