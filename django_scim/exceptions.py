
from .constants import SCHEMA_URI_ERROR

class SCIMException(Exception):
    status = 500
    schema = SCHEMA_URI_ERROR
    scim_type = None

    def __init__(self, detail=None, **kwargs):
        super(SCIMException, self).__init__()
        self.detail = detail or ''
        self.schemas = kwargs.get('schemas') or [self.schema]
        self.scim_type = kwargs.get('scim_type') or self.scim_type

    def to_dict(self):
        d = {
            'schemas': self.schemas,
            'detail': self.detail,
            'status': self.status,
        }
        if self.scim_type:
            d['scimType'] = self.scim_type

        return d


class NotFound(SCIMException):
    status = 404

    def __init__(self, uuid, **kwargs):
        detail_template = u'Resource {} not found'
        detail = detail_template.format(uuid)
        super(NotFound, self).__init__(detail, **kwargs)


class BadRequest(SCIMException):
    status = 400


class PatchError(SCIMException):
    status = 400


class IntegrityError(SCIMException):
    status = 409

