from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from django_scim.models import AbstractSCIMGroupMixin, AbstractSCIMUserMixin


class Company(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=100,
    )


class ScimUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, scim_username, password, **extra_fields):
        if not scim_username:
            raise ValueError('Users require a scim_usernamefield')
        user = self.model(scim_username=scim_username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, scim_username, password=None, **extra_fields):
        company, _ = Company.objects.get_or_create(name="Demo Inc")
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('company_id', company.id)
        return self._create_user(scim_username, password, **extra_fields)

    def create_superuser(self, scim_username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(scim_username, password, **extra_fields)


class User(AbstractSCIMUserMixin, TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    company = models.ForeignKey(
        'app.Company',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Why override this? Can't we just use what the AbstractSCIMUser mixin
    # gives us? The USERNAME_FIELD needs to be "unique" and for flexibility,
    # AbstractSCIMUser.scim_username is not unique by default.
    scim_username = models.CharField(
        _('SCIM Username'),
        max_length=254,
        null=True,
        blank=True,
        default=None,
        unique=True,
        help_text=_("A service provider's unique identifier for the user"),
    )

    email = models.EmailField(
        _('Email'),
    )

    first_name = models.CharField(
        _('First Name'),
        max_length=100,
    )

    last_name = models.CharField(
        _('Last Name'),
        max_length=100,
    )

    USERNAME_FIELD = 'scim_username'

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name + (' ' + self.last_name[0] if self.last_name else '')

    objects = ScimUserManager()


class Group(TimeStampedModel, AbstractSCIMGroupMixin):
    company = models.ForeignKey(
        'app.Company',
        on_delete=models.CASCADE,
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        through_fields=('group', 'user'),
    )

    @property
    def name(self):
        return self.scim_display_name


class GroupMembership(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(to='app.Group', on_delete=models.CASCADE)
