from django.conf.urls import url
from django.contrib.auth import get_user_model

from django_scim.models import SCIMUser
from django_scim.models import SCIMGroup
from django_scim.utils import get_group_model
from django_scim.views import UserSearchView
from django_scim.views import UserView
from django_scim.views import ObjView


urlpatterns = [
    url(r'^.search$',
        SearchView.as_view(),
        name='search'),

    url(r'^Users/.search$',
        UserSearchView.as_view(),
        name='users-search'),
    url(r'^Users$',
        UsersView.as_view(),
        name='users'),
    url(r'^Users/([^/]+)$',
        ObjView.as_view(scim_model_cls=SCIMUser, model_cls=get_user_model()),
        name='user'),

    url(r'^Groups/.search$',
        GroupsSearchView.as_view(),
        name='groups-search'),
    url(r'^Groups$',
        GroupsView.as_view(),
        name='groups'),
    url(r'^Groups/([^/]+)$',
        ObjView.as_view(scim_model_cls=SCIMGroup, model_cls=get_group_model()),
        name='group'),

    url(r'^Me$',
        MeView.as_view(),
        name='me'),

    url(r'^ServiceProviderConfig$',
        ServiceProviderConfigView.as_view(),
        name='service-provider-config'),

    url(r'^ResourceTypes$',
        ResourceTypesView.as_view(),
        name='resource-types'),

    url(r'^Schemas$',
        SchemasView.as_view(),
        name='schemas'),

    url(r'^Bulk$',
        BulkView.as_view(),
        name='bulk'),
]

