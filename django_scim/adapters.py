from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django import core
from six.moves.urllib.parse import urljoin

from .exceptions import PatchError
from .utils import get_base_scim_location_getter
from .utils import get_group_model


class SCIMMixin(object):
    def __init__(self, obj):
        self.obj = obj

    @property
    def id(self):
        return str(self.obj.id)

    @property
    def path(self):
        return reverse(self.url_name, kwargs={'uuid': self.obj.id})

    @property
    def location(self):
        return urljoin(get_base_scim_location_getter()(), self.path)

    def save(self):
        self.obj.save()

    def handle_operations(self, operations):
        for operation in operations:
            op_code = operation.get('op')
            op_code = 'handle_' + op_code
            handler = getattr(self, op_code)
            handler(operation)


class SCIMUser(SCIMMixin):
    # not great, could be more decoupled. But \__( )__/ whatevs.
    url_name = 'scim:users'
    resource_type = 'User'

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

        return dicts

    @property
    def meta(self):
        d = {
            'resourceType': self.resource_type,
            'created': self.obj.date_joined.isoformat(),
            'lastModified': self.obj.date_joined.isoformat(),
            'location': self.location,
        }

        return d

    def to_dict(self):
        d = {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
            'id': self.id,
            'userName': self.obj.username,
            'name': {
                'givenName': self.obj.first_name,
                'familyName': self.obj.last_name,
            },
            'displayName': self.display_name,
            'emails': self.emails,
            'active': self.obj.is_active,
            'groups': self.groups,
            'meta': self.meta,
        }

        return d

    def from_dict(self, d):
        username = d.get('userName')
        self.obj.username = username or ''

        first_name = d.get('name', {}).get('givenName')
        self.obj.first_name = first_name or ''

        last_name = d.get('name', {}).get('familyName')
        self.obj.last_name = last_name or ''

        emails = d.get('emails', [])
        primary_emails = [e['value'] for e in emails if e.get('primary')]
        emails = primary_emails + emails
        email = emails[0] if emails else None
        self.obj.email = email

        password = d.get('password')
        if password:
            self.obj.password = password

        active = d.get('active')
        if active is not None:
            self.obj.is_active = active

    @classmethod
    def resource_type_dict(self):
        id_ = self.resource_type
        path = reverse('scim:resource-types', kwargs={'uuid': id_})
        location = urljoin(get_base_scim_location_getter()(), path)
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ResourceType'],
            'id': id_,
            'name': 'User',
            'endpoint': reverse('scim:users'),
            'description': 'User Account',
            'schema': 'urn:ietf:params:scim:schemas:core:2.0:User',
            'meta': {
                'location': location,
                'resourceType': 'ResourceType'
            }
        }

    def handle_replace(self, operation):
        attr_map = {
            'familyName': 'last_name',
            'givenName': 'first_name',
            'userName': 'username',
            'active': 'is_active',
        }

        attrs = operation.get('value', {})

        for attr, attr_value in attrs.items():
            if attr in attr_map:
                setattr(self.obj, attr_map.get(attr), attr_value)
            elif attr == 'emails':
                primary_emails = [e for e in attr_value if e.get('primary')]
                if primary_emails:
                    email = primary_emails[0].get('value')
                elif attr_value:
                    email = attr_value[0].get('value')
                else:
                    raise PatchError('Invalid email value')

                try:
                    validator = core.validators.EmailValidator()
                    validator(email)
                except core.exceptions.ValidationError:
                    raise PatchError('Invalid email value')

                self.obj.email = email

            else:
                raise NotImplementedError('Not Implemented')

        self.obj.save()


class SCIMGroup(SCIMMixin):
    # not great, could be more decoupled. But \__( )__/ whatevs.
    url_name = 'scim:groups'
    resource_type = 'Group'

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

        return dicts

    @property
    def meta(self):
        d = {
            'resourceType': self.resource_type,
            'location': self.location,
        }

        return d

    def to_dict(self):
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:Group'],
            'id': self.id,
            'displayName': self.display_name,
            'members': self.members,
            'meta': self.meta,
        }

    def from_dict(self, d):
        name = d.get('displayName')
        self.obj.name = name or ''

    @classmethod
    def resource_type_dict(self):
        id_ = self.resource_type
        path = reverse('scim:resource-types', kwargs={'uuid': id_})
        location = urljoin(get_base_scim_location_getter()(), path)
        return {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:ResourceType'],
            'id': id_,
            'name': 'Group',
            'endpoint': reverse('scim:groups'),
            'description': 'Group',
            'schema': 'urn:ietf:params:scim:schemas:core:2.0:Group',
            'meta': {
                'location': location,
                'resourceType': 'ResourceType'
            }
        }

    def handle_add(self, operation):
        if operation.get('path') == 'members':
            members = operation.get('value', [])
            ids = [int(member.get('value')) for member in members]
            users = get_user_model().objects.filter(id__in=ids)

            if len(ids) != users.count():
                raise PatchError('Can not add a non-existent user to group')

            for user in users:
                self.obj.user_set.add(user)

        else:
            raise NotImplemented

    def handle_remove(self, operation):
        if operation.get('path') == 'members':
            members = operation.get('value', [])
            ids = [int(member.get('value')) for member in members]
            users = get_user_model().objects.filter(id__in=ids)

            if len(ids) != users.count():
                raise PatchError('Can not remove a non-existent user from group')

            for user in users:
                self.obj.user_set.remove(user)

        else:
            raise NotImplemented

    def handle_replace(self, operation):
        if operation.get('path') == 'name':
            name = operation.get('value')[0].get('value')
            self.obj.name = name
            self.obj.save()

        else:
            raise NotImplemented

