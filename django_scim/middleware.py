from django.urls import reverse
from django.http.response import HttpResponse

from .settings import scim_settings


class SCIMAuthCheckMiddleware(object):
    """
    Check to see if a prior middleware has logged the user in.

    This middleware should be place after auth middleware used to login a user.
    """

    def __init__(self, get_response=None):
        # One-time configuration and initialization.
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        # If we've just passed through the auth middleware and there is no user
        # associated with the request we can assume permission
        # was denied and return a 401.
        if not hasattr(request, 'user') or request.user.is_anonymous():
            if request.path.startswith(self.reverse_url):
                response = HttpResponse(status=401)
                response['WWW-Authenticate'] = scim_settings.WWW_AUTHENTICATE_HEADER
                return response

    @property
    def reverse_url(self):
        if not hasattr(self, '_reverse_url'):
            self._reverse_url = reverse('scim:root')
        return self._reverse_url
