class SCIMException(Exception):
    status = 500


class NotFound(SCIMException):
    status = 404


class BadRequest(SCIMException):
    status = 400


