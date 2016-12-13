from django.core.urlresolvers import reverse
from six.moves.urllib.parse import urljoin

from .auth import SCIMAuthBackendCollection
from .constants import DOCUMENTATION_URI
from .utils import get_base_scim_location_getter


class SCIMServiceProviderConfig(object):
    @property
    def authentication_schemes(self):
        backends = SCIMAuthBackendCollection.backends()
        return [backend.scheme_dict() for backend in backends]

    @property
    def meta(self):
        return {
            'location': self.location,
            'resourceType': 'ServiceProviderConfig',
        }

    @property
    def location(self):
        path = reverse('scim:service-provider-config')
        return urljoin(get_base_scim_location_getter()(), path)

    def to_dict(self):
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig'],
            'documentationUri': DOCUMENTATION_URI,
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
            'authenticationSchemes': self.authentication_schemes,
            'meta': self.meta,
        }

