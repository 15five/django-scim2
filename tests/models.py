from django.contrib.auth.models import AbstractUser
from django.db import connection, models

from django_scim import models as scim_models


class TestGroup(scim_models.AbstractSCIMGroupMixin):
    name = models.CharField('name', max_length=80, unique=True)

    class Meta:
        app_label = 'django_scim'


class TestUser(scim_models.AbstractSCIMUserMixin, AbstractUser):
    scim_groups = models.ManyToManyField(
        TestGroup,
        related_name="user_set",
    )

    class Meta:
        app_label = 'django_scim'


def get_group_model():
    return TestGroup
