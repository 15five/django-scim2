from django.conf.urls import url
from django.conf.urls import include

urlpatterns = [
    url(r'^scim/v2/', include('django_scim.urls', namespace='scim')),
]


