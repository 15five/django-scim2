import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import six

from .auth import SCIMRequest
from .filter import SCIMUserFilterTransformer
from .exceptions import SCIMException
from .exceptions import NotFound
from .exceptions import BadRequest
from .schemas import ALL as ALL_SCHEMAS
from .utils import get_group_adapter
from .utils import get_group_model
from .utils import get_user_adapter


SCIM_CONTENT_TYPE = 'application/scim+json'

SCHEMA_URI_SERACH_REQUEST = 'urn:ietf:params:scim:api:messages:2.0:SearchRequest'


class SCIMView(View):

    implemented = True

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if not self.implemented:
            return self.status_501(request, *args, **kwargs)

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
        return HttpResponse(content_type=SCIM_CONTENT_TYPE,
                            status=501)

    def auth_request(self, request, *args, **kwargs):
        SCIMRequest(request, *args, **kwargs).raise_auth_execptions()


class FilterMixin(object):

    parser = None
    scim_adapter = None

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
        qs = self.parser.search(query)
        return self._build_response(qs, start, count)

    def _build_response(self, qs, start, count):
        try:
            total_count = sum(1 for _ in qs)
            qs = qs[start-1:(start-1) + count]
            resources = [self.scim_adapter(u).to_dict() for u in qs]
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


class SearchView(FilterMixin, SCIMView):
    http_method_names = ['post']

    def post(self, request):
        body = json.loads(request.body or '{}')
        if body.get('schemas') != [SCHEMA_URI_SERACH_REQUEST]:
            raise BadRequest('Invalid schema uri. Must be SearchRequest.')

        query = body.get('filter', request.GET.get('filter'))

        if not query:
            raise BadRequest('No filter query specified')
        else:
            return self._search(query, *self._page(request))


class UsersView(FilterMixin, SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    scim_adapter = get_user_adapter()
    model_cls = get_user_model()
    parser = SCIMUserFilterTransformer

    def get(self, request, uuid=None):
        if uuid:
            return self.get_single(request, uuid)

        return self.get_many(request)

    def get_single(self, request, uuid):
        try:
            obj = self.scim_adapter(self.model_cls.objects.get(id=uuid))
        except ObjectDoesNotExist as e:
            raise NotFound(e)
        else:
            return HttpResponse(content=json.dumps(obj.to_dict(), encoding='utf-8'),
                                content_type=SCIM_CONTENT_TYPE)

    def get_many(self, request):
        query = request.GET.get('filter')
        if query:
            return self._search(query, *self._page(request))

        qs = self.model_cls.objects.all().order_by('id')
        return self._build_response(qs, *self._page(request))


class GroupsView(SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    scim_adapter = get_group_adapter()
    model_cls = get_group_model()


class ServiceProviderConfigView(SCIMView):
    http_method_names = ['get']

    def get(self):
        config = ServiceProviderConfig()
        return HttpResponse(content=json.dumps(config.to_dict(), encoding='utf-8'),
                            content_type=SCIM_CONTENT_TYPE)


class ResourceTypesView(SCIMView):

    http_method_names = ['get']

    @property
    def type_dict_by_type_id(self):
        type_adapters = get_user_adapter(), get_group_adapter()
        type_dicts = [m.resource_type_dict() for m in type_adapters]
        return {d['id'] for d in type_dicts}

    def get(self, request, uuid=None, *args, **kwargs):
        if type_id:
            doc = self.type_dict_by_type_id.get(uuid)
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

    def get(self, uuid=None, *args, **kwargs):
        if type_id:
            doc = self.schemas_by_uri.get(uuid)
            if not doc:
                return HttpResponse(content_type=SCIM_CONTENT_TYPE,
                                    status=404)
        else:
            doc = self.type_dicts

        return HttpResponse(content=json.dumps(doc, encoding='utf-8'),
                            content_type=SCIM_CONTENT_TYPE)

