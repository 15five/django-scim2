from unittest import mock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from django_scim.middleware import SCIMAuthCheckMiddleware


class SCIMMiddlewareTestCase(TestCase):
    def test_middleware_for_django2(self):
        """
        Regression test for https://github.com/15five/django-scim2/issues/13
        """
        middleware = SCIMAuthCheckMiddleware()

        request = RequestFactory().get(middleware.reverse_url)
        request.user = AnonymousUser()

        response = middleware.process_request(request)
        self.assertEqual(response.status_code, 401)

    @mock.patch('django_scim.middleware.SCIMAuthCheckMiddleware.log_call')
    def test_log_called_only_for_scim_calls(self, log_call_func):
        middleware = SCIMAuthCheckMiddleware()

        request = RequestFactory().get('/')
        middleware.process_response(request, None)
        log_call_func.assert_not_called()

        request = RequestFactory().get(middleware.reverse_url)
        middleware.process_response(request, None)
        log_call_func.assert_called()

