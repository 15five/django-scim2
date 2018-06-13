from .constants import SchemaURI

class SCIMException(Exception):
    status = 500
    schema = SchemaURI.ERROR
    scim_type = None

    def __init__(self, detail=None, **kwargs):
        super().__init__()
        self.detail = detail or ''
        self.status = kwargs.get('status') or self.status
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


class NotFoundError(SCIMException):
    status = 404

    def __init__(self, uuid, **kwargs):
        detail_template = u'Resource {} not found'
        detail = detail_template.format(uuid)
        super().__init__(detail, **kwargs)


class BadRequestError(SCIMException):
    status = 400


class PatchError(SCIMException):
    status = 400


class IntegrityError(SCIMException):
    status = 409
