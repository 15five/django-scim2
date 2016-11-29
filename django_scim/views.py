import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import six

from .filter import SCIMUserFilterTransformer
from .models import SCIMUser
from .exceptions import SCIMException
from .exceptions import NotFound
from .auth import SCIMRequest
from .schemas import ALL as ALL_SCHEMAS


SCIM_CONTENT_TYPE = 'application/scim+json'


class SCIMView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            self.auth_request(request, *args, **kwargs)
            return super(SCIMView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            if not isinstance(e, SCIMException):
                e = SCIMException(six.text_type(e))

            resp = HttpResponse(content_type=SCIM_CONTENT_TYPE,
                                status=e.status)
            resp.content = json.dumps({
                'Errors': [
                    {
                        'description': six.text_type(e),
                        'code': e.status
                    }
                ]
            }, encoding='utf-8')
            return resp

    def status_501(self, request, *args, **kwargs):
        """
        A service provider that does NOT support a feature SHOULD
        respond with HTTP status code 501 (Not Implemented).
        """
        return HttpResponse(content=json.dumps({}, encoding='utf-8'),
                            content_type=SCIM_CONTENT_TYPE,
                            status=501)

    def auth_request(self, request, *args, **kwargs):
        SCIMRequest(request, *args, **kwargs).raise_auth_execptions()


class SearchView(SCIMView):
    http_method_names = ['post']

    def get(self, request):
        return self._search(request.GET.get('filter'), *self._page(request))

    def post(self, request):
        body = json.loads(request.body or '{}')
        query = body.get('filter', request.GET.get('filter'))
        if not query:
            raise BadRequest('No filter query specified')
        else:
            return self._search(query, *self._page(request))

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


class ObjView(SCIMView):
    http_method_names = ['get']

    scim_model_cls = None
    model_cls = None

    def get(self, request, uuid):
        try:
            obj = self.scim_model_cls(self.model_cls.objects.get(id=uuid))
        except ObjectDoesNotExist as e:
            raise NotFound(e)
        else:
            return HttpResponse(content=json.dumps(obj.to_dict(), encoding='utf-8'),
                                content_type=SCIM_CONTENT_TYPE)


class UsersSearchView(SearchView):

    scim_model_cls = SCIMUser
    parser = SCIMUserFilterTransformer

    def _search(self, query, start, count):
        try:
            qs = self.parser.search(query)
            total_count = sum(1 for _ in qs)
            qs = qs[start-1:(start-1) + count]
            resources = [self.scim_model_cls(u).to_dict() for u in qs]
            doc = {
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
                'totalResults': total_count,
                'itemsPerPage': count,
                'startIndex': start,
                'Resources': resources,
            }
        except ValueError as e:
            raise BadRequest(e)
        else:
            return HttpResponse(content=json.dumps(doc, encoding='utf-8'),
                                content_type=SCIM_CONTENT_TYPE)


class UsersView(SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']



class GroupsSearchView(SearchView):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(GroupsSearchView, self).status_501(request, *args, **kwargs)


class GroupsView(SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']



class MeView(SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(MeView, self).status_501(request, *args, **kwargs)


class ServiceProviderConfigView(SCIMView):

    http_method_names = ['get']

    def get(self):
        config = ServiceProviderConfig()
        return HttpResponse(content=json.dumps(config.to_dict(), encoding='utf-8'),
                            content_type=SCIM_CONTENT_TYPE)


class ResourceTypesView(SCIMView):

    http_method_names = ['get']

    type_models = SCIMUser, SCIMGroup
    type_dicts = [m.resource_type_dict() for m in type_models]
    type_dict_by_type_id = {d['id'] for d in type_dicts}

    def get(self, request, type_id=None, *args, **kwargs):
        if type_id:
            doc = self.type_dict_by_type_id.get(type_id)
            if not doc:
                return HttpResponse(content_type=SCIM_CONTENT_TYPE,
                                    status=404)
        else:
            doc = self.type_dicts

        return HttpResponse(content=json.dumps(doc, encoding='utf-8'),
                            content_type=SCIM_CONTENT_TYPE)


class SchemasView(SCIMView):

    http_method_names = ['get']

    schemas_by_uri = {s['id']: s for s in ALL_SCHEMAS}

    def get(self, type_id=None, *args, **kwargs):
        if type_id:
            doc = self.schemas_by_uri.get(type_id)
            if not doc:
                return HttpResponse(content_type=SCIM_CONTENT_TYPE,
                                    status=404)
        else:
            doc = self.type_dicts

        return HttpResponse(content=json.dumps(doc, encoding='utf-8'),
                            content_type=SCIM_CONTENT_TYPE)


class BulkView(SCIMView):

    http_method_names = ['post']

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(MeView, self).status_501(request, *args, **kwargs)

