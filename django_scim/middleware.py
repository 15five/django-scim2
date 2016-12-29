from django.core.urlresolvers import reverse
from django.http.response import HttpResponse

# bastb Django 1.10 has updated Middleware. This code imports the Mixin required to get old-style
# middleware working again
# More?
#  https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
try:
    from django.utils.deprecation import MiddlewareMixin
    middleware_parent_class = MiddlewareMixin
except ImportError:
    middleware_parent_class = object

from .settings import scim_settings


class SCIMAuthCheckMiddleware(middleware_parent_class):
    """
    Check to see if a prior middleware has logged the user in.

    This middleware should be place after auth middleware used to login a user.
    """
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

