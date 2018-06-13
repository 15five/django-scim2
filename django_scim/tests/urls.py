try:
    from django.urls import re_path
    from django.urls import include
except ImportError:
    from django.conf.urls import url as re_path
    from django.conf.urls import include

urlpatterns = [
    re_path(r'^scim/v2/', include('django_scim.urls')),
]
