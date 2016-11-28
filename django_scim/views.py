"""
Resource Endpoint         Operations             Description
-------- ---------------- ---------------------- --------------------
User     /Users           GET (Section 3.4.1),   Retrieve, add,
                          POST (Section 3.3),    modify Users.
                          PUT (Section 3.5.1),
                          PATCH (Section 3.5.2),
                          DELETE (Section 3.6)

Group    /Groups          GET (Section 3.4.1),   Retrieve, add,
                          POST (Section 3.3),    modify Groups.
                          PUT (Section 3.5.1),
                          PATCH (Section 3.5.2),
                          DELETE (Section 3.6)

Self     /Me              GET, POST, PUT, PATCH, Alias for operations
                          DELETE (Section 3.11)  against a resource
                                                 mapped to an
                                                 authenticated
                                                 subject (e.g.,
                                                 User).

Service  /ServiceProvider GET (Section 4)        Retrieve service
provider Config                                  provider's
config.                                          configuration.

Resource /ResourceTypes   GET (Section 4)        Retrieve supported
type                                             resource types.

Schema   /Schemas         GET (Section 4)        Retrieve one or more
                                                 supported schemas.

Bulk     /Bulk            POST (Section 3.7)     Bulk updates to one
                                                 or more resources.

Search   [prefix]/.search POST (Section 3.4.3)   Search from system
                                                 root or within a
                                                 resource endpoint
                                                 for one or more
                                                 resource types using
                                                 POST.
"""
import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import six

from django_scim.filter import SCIMUserFilterTransformer
from django_scim.models import SCIMUser
from django_scim.exceptions import SCIMException
from django_scim.exceptions import NotFound
from django_scim.exceptions import BadRequest


class SCIMView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(SCIMView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            if not isinstance(e, SCIMException):
                e = SCIMException(str(e))

            resp = HttpResponse(content_type='application/json; charset=utf-8',
                                status=e.status)
            resp.content = json.dumps({
                'Errors': [
                    {
                        'description': unicode(e),
                        'code': e.status
                    }
                ]
            }, encoding='utf-8')
            return resp


class SearchView(SCIMView):
    pass




class ObjView(SCIMView):
    scim_model_cls = None
    model_cls = None

    http_method_names = ['get']

    def get(self, request, uuid):
        try:
            obj = self.scim_model_cls(self.model_cls.objects.get(id=uuid))
        except ObjectDoesNotExist as e:
            raise NotFound(e)
        else:
            return HttpResponse(json.dumps(obj.to_dict(), encoding='utf-8'),
                                content_type='application/json; charset=utf-8')


class UsersSearchView(SCIMView):
    model_cls = SCIMUser
    parser = SCIMUserFilterTransformer

    def _page(self, request):
        try:
            start = request.GET.get('startIndex', 1)
            if start is not None:
                start = int(start)
                if start < 1:
                    raise BadRequest('Invalid startIndex (must be >= 1)')

            count = request.GET.get('count', 50)
            if count is not None:
                count = int(count)
            return start, count

        except ValueError as e:
            raise BadRequest('Invalid pagination values: ' + str(e))

    def _search(self, query, start, count):
        try:
            qs = self.parser.search(query)
            resources = [self.model_cls(u).to_dict() for u in qs[start-1:(start-1) + count]]
            doc = {
                'totalResults': sum((1 for _ in qs)),
                'itemsPerPage': count,
                'startIndex': start,
                'schemas': ['urn:scim:schemas:core:2.0'],
                'Resources': resources,
            }
        except ValueError as e:
            raise BadRequest(e)
        else:
            return HttpResponse(json.dumps(doc, encoding='utf-8'),
                                content_type='application/json; charset=utf-8')

    def get(self, request):
        return self._search(request.GET.get('filter'), *self._page(request))

    def post(self, request):
        body = json.loads(request.body or '{}')
        query = body.get('filter', request.GET.get('filter'))
        if not query:
            raise BadRequest('No filter query specified')
        else:
            return self._search(query, *self._page(request))


class UsersView(SCIMView):
    pass


class GroupsSearchView(SCIMView):
    pass


class GroupsView(SCIMView):
    pass


class MeView(SCIMView):
    A service provider that does NOT support this feature SHOULD
          respond with HTTP status code 501 (Not Implemented).
    pass


class ServiceProviderConfigView(SCIMView):
    pass


class ResourceTypesView(SCIMView):
    pass


class SchemasView(SCIMView):
    pass


class BulkView(SCIMView):
    pass

