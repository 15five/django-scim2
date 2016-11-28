from django.core.urlresolvers import reverse
from django.utils.timezone import utc
from six.moves.urllib.parse import urljoin

from .constants import BASE_SCIM_LOCATION


class SCIMMixin(object):
    def __init__(self, obj):
        self.obj = obj

    @property
    def id(self):
        return str(self.obj.id)

    @property
    def path(self):
        return reverse(self.url_name, args=(self.obj.id,))

    @property
    def location(self):
        return urljoin(BASE_SCIM_LOCATION, self.path)


class SCIMUser(SCIMMixin):
    # not great, could be more decoupled. But \__( )__/ whatevs.
    url_name = 'scim-user'

    @property
    def display_name(self):
        if self.obj.first_name and self.obj.last_name:
            return u'{0.first_name} {0.last_name}'.format(self.obj)
        return self.obj.username

    @property
    def emails(self):
        return [{'value': self.obj.email, 'primary': True}]

    @property
    def groups(self):
        scim_groups = [SCIMGroup(group) for group in self.obj.groups.all()]

        dicts = []
        for group in scim_groups:
            d = {
                'value': group.id,
                '$ref': group.location,
                'display': group.display_name,
            }
            dicts.append(d)

        return d

    @property
    def meta(self):
        d = {
            'resourceType': 'User',
            'created': utc.localize(self.obj.date_joined).isoformat(),
            'lastModified': utc.localize(self.obj.date_joined).isoformat(),
            'location': self.location,
        }

        return d

    def to_dict(self):
        d = {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
            'id': self.id,
            'userName': self.obj.username,
            'name': {
                'formatted': self.display_name,
                'familyName': self.obj.last_name,
                'givenName': self.obj.first_name,
            },
            'displayName': self.display_name,
            'emails': self.emails,
            'active': self.obj.is_active,
            'groups': self.groups,
            'meta': self.meta,
        }

        return d


class SCIMGroup(SCIMMixin):
    # not great, could be more decoupled. But \__( )__/ whatevs.
    url_name = 'scim-group'

    @property
    def display_name(self):
        return self.obj.name

    @property
    def members(self):
        users = self.obj.user_set.all()
        scim_users = [SCIMUser(user) for user in users]

        dicts = []
        for user in scim_users:
            d = {
                'value': user.id,
                '$ref': user.location,
                'display': user.display_name,
            }
            dicts.append(d)

        return d

    @property
    def meta(self):
        d = {
            'resourceType': 'Group',
            'location': self.location,
        }

        return d

    def to_dict(self):
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:Group'],
            'id': self.id,
            'displayName': self.obj.name,
            'members': self.members,
            'meta': self.meta,
        }

