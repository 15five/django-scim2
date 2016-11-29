from django.conf.urls import url
from django.conf.urls import include
from django.contrib.auth import get_user_model

from .constants import BASE_URL_REGEX
from .models import SCIMUser
from .models import SCIMGroup
from .utils import get_group_model
from .views import UserSearchView
from .views import UserView
from .views import ObjView


class SCIMUrls(object):
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

        url(r'^ResourceTypes/([^/]+)$',
            ResourceTypesView.as_view(),
            name='resource-type'),

        url(r'^Schemas$',
            SchemasView.as_view(),
            name='schemas'),

        url(r'^Bulk$',
            BulkView.as_view(),
            name='bulk'),
    ]


urlpatterns = [
    url(BASE_URL_REGEX, include(SCIMUrls, namespace='scim')),
]

