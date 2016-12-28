from django.core.urlresolvers import reverse
from six.moves.urllib.parse import urljoin

from .settings import scim_settings
from .utils import get_base_scim_location_getter


class SCIMServiceProviderConfig(object):
    """
    A reference ServiceProviderConfig. This should be overridden to
    describe those authentication_schemes and features that are implemented by
    your app.
    """
    def __init__(self, request=None):
        self.request = request

    @property
    def meta(self):
        return {
            'location': self.location,
            'resourceType': 'ServiceProviderConfig',
        }

    @property
    def location(self):
        path = reverse('scim:service-provider-config')
        return urljoin(get_base_scim_location_getter()(self.request), path)

    def to_dict(self):
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig'],
            'documentationUri': scim_settings.DOCUMENTATION_URI,
            'patch': {
                'supported': True,
            },
            'bulk': {
                'supported': False,
                'maxOperations': 1000,
                'maxPayloadSize': 1048576,
            },
            'filter': {
                'supported': True,
                'maxResults': 50,
            },
            'changePassword': {
                'supported': True,
            },
            'sort': {
                'supported': False,
            },
            'etag': {
                'supported': False,
            },
            'authenticationSchemes': scim_settings.AUTHENTICATION_SCHEMES,
            'meta': self.meta,
        }

