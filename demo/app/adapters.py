import copy
import logging
import re

import django
from django import core
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Prefetch
from django.utils.functional import cached_property
from django_scim import exceptions as scim_exceptions
from django_scim.adapters import SCIMUser, SCIMGroup
from django_scim.constants import SchemaURI
from django_scim.utils import get_group_adapter, get_group_model

from app import constants
from app.models import User, Group


logger = logging.getLogger(__name__)


class SCIMUser(SCIMUser):

    password_changed = False
    activity_changed = False

    def __init__(self, obj, request=None):
        super().__init__(obj, request)

        self._from_dict_copy = None

    @property
    def is_new_user(self):
        return not bool(self.obj.id)

    @property
    def display_name(self):
        """
        Return the displayName of the user per the SCIM spec.
        """
        if self.obj.first_name and self.obj.last_name:
            return f'{self.obj.first_name} {self.obj.last_name}'
        return self.obj.email

    @property
    def groups(self):
        """
        Return the groups of the user per the SCIM spec.
        """

        group_qs = Group.objects.filter(members__member=self.obj)
        scim_groups = [get_group_adapter()(g, self.request) for g in group_qs]

        dicts = []
        for group in scim_groups:
            d = {
                'value': group.scim_id,
                '$ref': group.location,
                'display': group.display_name,
            }
            dicts.append(d)

        return dicts

    @property
    def meta(self):
        """
        Return the meta object of the user per the SCIM spec.
        """
        d = {
            'resourceType': self.resource_type,
            'created': self.obj.create_ts.isoformat(timespec='milliseconds'),
            'lastModified': self.obj.update_ts.isoformat(timespec='milliseconds'),
            'location': self.location,
        }

        return d

    def to_dict(self):
        """
        Return a ``dict`` conforming to the SCIM User Schema,
        ready for conversion to a JSON object.
        """
        d = super().to_dict()
        d.update({
            'userName': self.obj.scim_username,
            constants.SCHEMA_URI_APP_USER: {
                'companyId': self.obj.company_id,
            },
        })

        return d

    def from_dict(self, d):
        """
        Consume a ``dict`` conforming to the SCIM User Schema, updating the
        internal user object with data from the ``dict``.

        Please note, the user object is not saved within this method. To
        persist the changes made by this method, please call ``.save()`` on the
        adapter. Eg::

            scim_user.from_dict(d)
            scim_user.save()
        """
        # Store dict for possible later use when saving user
        self._from_dict_copy = copy.deepcopy(d)

        self.obj.company_id = self.request.user.company_id

        self.parse_active(d.get('active'))

        self.obj.first_name = d.get('name', {}).get('givenName') or ''

        self.obj.last_name = d.get('name', {}).get('familyName') or ''

        self.parse_email(d.get('emails'))

        if self.is_new_user and not self.obj.email:
            raise scim_exceptions.BadRequestError('Empty email value')

        self.obj.scim_username = d.get('userName')
        self.obj.scim_external_id = d.get('externalId') or ''

        cleartext_password = d.get('password')
        if cleartext_password:
            self.obj.set_password(cleartext_password)
            self.obj._scim_cleartext_password = cleartext_password
            self.password_changed = True

    def parse_active(self, active):
        if active is not None:
            if active != self.obj.is_active:
                self.activity_changed = True
            self.obj.is_active = active

    def parse_email(self, emails_value):
        if emails_value:
            email = None
            if isinstance(emails_value, list):
                primary_emails = [e['value'] for e in emails_value if e.get('primary')]
                other_emails = [e['value'] for e in emails_value if not e.get('primary')]
                # Make primary emails the first in the list
                sorted_emails = list(map(str.strip, primary_emails + other_emails))
                email = sorted_emails[0] if sorted_emails else None
            elif isinstance(emails_value, dict):
                # if value is a dict, let's assume it contains the primary email.
                # OneLogin sends a dict despite the spec:
                #   https://tools.ietf.org/html/rfc7643#section-4.1.2
                #   https://tools.ietf.org/html/rfc7643#section-8.2
                email = (emails_value.get('value') or '').strip()

            self.validate_email(email)

            self.obj.email = email

    @staticmethod
    def validate_email(email):
        try:
            validator = core.validators.EmailValidator()
            validator(email)
        except core.exceptions.ValidationError:
            raise scim_exceptions.BadRequestError('Invalid email value')

    def save(self):
        temp_password = None
        if self.is_new_user:
            password = getattr(self.obj, '_scim_cleartext_password', None)
            # If temp password was not passed, create one.
            if password is None:
                self.obj.require_password_change = True
                temp_password = generate_temp_password()
                password = temp_password
            self.obj.set_password(password)

        is_new_user = self.is_new_user
        try:
            with transaction.atomic():
                super().save()
                if is_new_user:
                    # Set SCIM ID to be equal to database ID. Because users are uniquely identified with this value
                    # its critical that changes to this line are well considered before executed.
                    self.obj.__class__.objects.update(scim_id=str(self.obj.id))
                logger.info(f'User saved. User id {self.obj.id}')
        except Exception as e:
            raise self.reformat_exception(e)

    def delete(self):
        self.obj.is_active = False
        self.obj.save()
        logger.info(f'Deactivated user id {self.obj.id}')

    def handle_add(self, path, value, operation):
        if path == 'externalId':
            self.obj.scim_external_id = value
            self.obj.save()

    def handle_replace(self, path, value, operation):
        """
        Handle the replace operations.

        All operations happen within an atomic transaction.
        """
        attr_map = {
            'familyName': 'last_name',
            'givenName': 'first_name',
            'active': 'is_active',
            'userName': 'scim_username',
            'externalId': 'scim_external_id',
        }

        for attr, attr_value in (value or {}).items():
            if attr in attr_map:
                setattr(self.obj, attr_map.get(attr), attr_value)

            elif attr == 'emails':
                self.parse_email(attr_value)

            elif attr == 'password':
                self.obj.set_password(attr_value)

            else:
                raise scim_exceptions.SCIMException('Not Implemented', status=409)

        self.obj.save()

    @classmethod
    def resource_type_dict(cls, request=None):
        d = super().resource_type_dict(request)
        d['schemaExtensions'] = [
            {
                'schema': constants.SCHEMA_URI_APP_USER,
                'required': False,
            },
        ]
        return d

