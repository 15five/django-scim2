from django.core.urlresolvers import reverse
from six.moves.urllib.parse import urljoin

from .auth import SCIMAuthBackendCollection
from .constants import BASE_SCIM_LOCATION
from .constants import DOCUMENTATION_URI


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
        return urljoin(BASE_SCIM_LOCATION, path)

    def to_dict(self):
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig'],
            'documentationUri': DOCUMENTATION_URI,
            'patch': {
                'supported': True,
            },
            'bulk': {
                'supported': False,
            },
            'filter': {
                'supported': True,
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

