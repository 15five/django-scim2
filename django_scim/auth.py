from django.conf import settings
from django.utils.module_loading import import_string


class SCIMExampleAuth(object):
    """
    Example auth class. Given a request and its args/kwargs,
    this class can authenticate and authorize the request.
    """

    type = 'httpbasic'
    name = 'Http Basic'
    description = 'Authentication scheme using the HTTP Basic Standard'
    spec_uri = 'http://www.rfc-editor.org/info/rfc2617'
    documentation_uri = 'http://exmaple.com/docs.html'

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def raise_auth_exceptions(self):
        """
        To reject a request for whatever reason, raise an exception.
        To allow a request, do nothing.
        """
        # raise errors in here
        # exceptions need a 'status' attr and must be castable to a string.
        pass

    @classmethod
    def scheme_dict(cls):
        return {
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'specUri': self.spec_uri,
            'documentationUri': self.documentation_uri,
        }


class SCIMAuthBackendCollection(object):

    _backends = None

    @classmethod
    def backends(cls):
        if cls._backends is None:
            cls_strings = getattr(settings, 'DJANGO_SCIM_AUTH_BACKENDS', [])
            cls._backends = []
            for string in cls_strings:
               cls._backends.append(import_string(string))
        return cls._backends


class SCIMRequest(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def raise_auth_execptions(self):
        for backend in SCIMAuthBackendCollection.backends():
            b = backend(self.request, *self.request.args, **self.request.kwargs)
            b.raise_auth_exceptions()

