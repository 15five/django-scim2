from django.conf.urls import patterns, url

from django_scim.models import SCIMUser
from django_scim.views import SearchView, UserView


urlpatterns = patterns('',
    url(r'^!?api/internal/scim/v2/Users/.search/?$',
        SearchView.as_view(usercls=SCIMUser), name='scim-search'),
    url(r'^!?api/internal/scim/v2/Users/([^/]+)$',
        UserView.as_view(usercls=SCIMUser), name='scim-user'),
)
