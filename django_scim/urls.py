from django.conf.urls import url
from django.conf.urls import include

from .filters import SCIMUserFilterTransformer
from .utils import get_user_adapter
from . import views


urlpatterns = [
    # This endpoint is used soley for middleware url purposes.
    url(r'^$',
        views.SCIMView.as_view(implemented=False),
        name='root'),

    url(r'^.search$',
        views.SearchView.as_view(implemented=False),
        name='search'),

    url(r'^Users/.search$',
        views.SearchView.as_view(scim_adapter=get_user_adapter(), parser=SCIMUserFilterTransformer),
        name='users-search'),

    url(r'^Users(?:/(?P<uuid>[^/]+))?$',
        views.UsersView.as_view(),
        name='users'),

    url(r'^Groups/.search$',
        views.SearchView.as_view(implemented=False),
        name='groups-search'),

    url(r'^Groups(?:/(?P<uuid>[^/]+))?$',
        views.GroupsView.as_view(),
        name='groups'),

    url(r'^Me$',
        views.SCIMView.as_view(implemented=False),
        name='me'),

    url(r'^ServiceProviderConfig$',
        views.ServiceProviderConfigView.as_view(),
        name='service-provider-config'),

    url(r'^ResourceTypes(?:/(?P<uuid>[^/]+))?$',
        views.ResourceTypesView.as_view(),
        name='resource-types'),

    url(r'^Schemas(?:/(?P<uuid>[^/]+))?$',
        views.SchemasView.as_view(),
        name='schemas'),

    url(r'^Bulk$',
        views.SCIMView.as_view(implemented=False),
        name='bulk'),
]

