import pytz
from django.conf import settings
from django.core.urlresolvers import reverse


def to_utc(date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return local_tz.localize(date).astimezone(pytz.utc)


class SCIMUser(object):
    def __init__(self, user):
        self.user = user

    @property
    def display_name(self):
        if self.user.first_name and self.user.last_name:
            return u'{0.first_name} {0.last_name}'.format(self.user)
        return self.user.username

    @property
    def emails(self):
        return {self.user.email: True}

    def to_dict(self):
        d = {
            'schemas': ['urn:scim:schemas:core:1.0'],
            'id': str(self.user.id),
            'userName': self.user.username,
            'name': {
                'formatted': self.display_name,
                'familyName': self.user.last_name,
                'givenName': self.user.first_name,
            },
            'displayName': self.display_name,
            'emails': [{'value': email, 'primary': primary}
                       for email, primary in self.emails.iteritems()],
            'active': self.user.is_active,
            'groups': [],
            'meta': {
                'created': to_utc(self.user.date_joined).isoformat(),
                'lastModified': to_utc(self.user.date_joined).isoformat(),
                'location': reverse('scim-user', args=(self.user.id,))
            }
        }

        return d
