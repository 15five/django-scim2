from django.conf.urls import include, url

from django_scim.urls import urlpatterns as scim_urls


urlpatterns = [
    url(r'^scim/v2/', include(scim_urls, namespace='scim')),
]

