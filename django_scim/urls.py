from django.conf.urls import url
from django.conf.urls import include
from django.contrib.auth import get_user_model

from .constants import BASE_URL_REGEX
from .models import SCIMUser
from .models import SCIMGroup
from .utils import get_group_model
from . import views


class SCIMUrls(object):
    urlpatterns = [
        url(r'^.search$',
            views.SearchView.as_view(),
            name='search'),

        url(r'^Users/.search$',
            views.UsersSearchView.as_view(),
            name='users-search'),

        url(r'^Users$',
            views.UsersView.as_view(),
            name='users'),

        url(r'^Users/([^/]+)$',
            views.ObjView.as_view(scim_model_cls=SCIMUser, model_cls_getter=get_user_model),
            name='user'),

        url(r'^Groups/.search$',
            views.GroupsSearchView.as_view(),
            name='groups-search'),

        url(r'^Groups$',
            views.GroupsView.as_view(),
            name='groups'),

        url(r'^Groups/([^/]+)$',
            views.ObjView.as_view(scim_model_cls=SCIMGroup, model_cls_getter=get_group_model),
            name='group'),

        url(r'^Me$',
            views.MeView.as_view(),
            name='me'),

        url(r'^ServiceProviderConfig$',
            views.ServiceProviderConfigView.as_view(),
            name='service-provider-config'),

        url(r'^ResourceTypes$',
            views.ResourceTypesView.as_view(),
            name='resource-types'),

        url(r'^ResourceTypes/([^/]+)$',
            views.ResourceTypesView.as_view(),
            name='resource-type'),

        url(r'^Schemas$',
            views.SchemasView.as_view(),
            name='schemas'),

        url(r'^Schemas/([^/]+)$',
            views.SchemasView.as_view(),
            name='schemas'),

        url(r'^Bulk$',
            views.BulkView.as_view(),
            name='bulk'),
    ]


urlpatterns = [
    url(BASE_URL_REGEX, include(SCIMUrls, namespace='scim')),
]

