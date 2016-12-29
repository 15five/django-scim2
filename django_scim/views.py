import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django import db
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import six
from django.utils.decorators import method_decorator
from django.utils.six.moves.urllib.parse import urljoin

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from .constants import SCIM_CONTENT_TYPE
from .constants import SCHEMA_URI_SERACH_REQUEST
from .filters import SCIMUserFilterTransformer
from .exceptions import SCIMException
from .exceptions import NotFound
from .exceptions import BadRequest
from .exceptions import IntegrityError
from django_scim.schemas import ALL as ALL_SCHEMAS
from .utils import get_group_adapter
from .utils import get_group_model
from .utils import get_user_adapter
from .utils import get_base_scim_location_getter
from .utils import get_service_provider_config_model


class SCIMView(View):

    implemented = True

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.implemented:
            return self.status_501(request, *args, **kwargs)

        try:
            return super(SCIMView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            if not isinstance(e, SCIMException):
                e = SCIMException(six.text_type(e))

            content = json.dumps(e.to_dict())
            return HttpResponse(content=content,
                                content_type=SCIM_CONTENT_TYPE,
                                status=e.status)

    def status_501(self, request, *args, **kwargs):
        """
        A service provider that does NOT support a feature SHOULD
        respond with HTTP status code 501 (Not Implemented).
        """
        return HttpResponse(content_type=SCIM_CONTENT_TYPE, status=501)


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

    def _search(self, request, query, start, count):
        try:
            qs = self.parser.search(query)
        except ValueError as e:
            raise BadRequest('Invalid filter/search query: ' + str(e))

        return self._build_response(request, qs, start, count)

    def _build_response(self, request, qs, start, count):
        try:
            total_count = sum(1 for _ in qs)
            qs = qs[start-1:(start-1) + count]
            resources = [self.scim_adapter(o, request=request).to_dict() for o in qs]
            doc = {
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
                'totalResults': total_count,
                'itemsPerPage': count,
                'startIndex': start,
                'Resources': resources,
            }
        except ValueError as e:
            raise BadRequest(six.text_type(e))
        else:
            content = json.dumps(doc)
            return HttpResponse(content=content,
                                content_type=SCIM_CONTENT_TYPE)


class SearchView(FilterMixin, SCIMView):
    http_method_names = ['post']

    scim_adapter = None

    def post(self, request):
        body = json.loads(request.body.decode() or '{}')
        if body.get('schemas') != [SCHEMA_URI_SERACH_REQUEST]:
            raise BadRequest('Invalid schema uri. Must be SearchRequest.')

        query = body.get('filter', request.GET.get('filter'))

        if not query:
            raise BadRequest('No filter query specified')
        else:
            response = self._search(request, query, *self._page(request))
            path = reverse(self.scim_adapter.url_name)
            url = urljoin(get_base_scim_location_getter()(request=request), path).rstrip('/')
            response['Location'] = url + '/.search'
            return response


class GetView(object):
    def get(self, request, uuid=None):
        if uuid:
            return self.get_single(request, uuid)

        return self.get_many(request)

    def get_single(self, request, uuid):
        try:
            scim_obj = self.scim_adapter(
                obj=self.model_cls.objects.get(id=uuid),
                request=request,
            )
        except ObjectDoesNotExist as _e:
            raise NotFound(uuid)
        else:
            content = json.dumps(scim_obj.to_dict())
            response = HttpResponse(content=content,
                                    content_type=SCIM_CONTENT_TYPE)
            response['Location'] = scim_obj.location
            return response

    def get_many(self, request):
        query = request.GET.get('filter')
        if query:
            return self._search(request, query, *self._page(request))

        qs = self.model_cls.objects.all().order_by('id')
        return self._build_response(request, qs, *self._page(request))


class DeleteView(object):
    def delete(self, request, uuid):
        obj_qs = self.model_cls.objects.filter(id=uuid)

        if obj_qs.exists():
            obj_qs.delete()
            return HttpResponse(status=204)
        else:
            raise NotFound(uuid)


class PostView(object):
    def post(self, request, **kwargs):
        obj = self.model_cls()
        scim_obj = self.scim_adapter(obj, request=request)

        body = json.loads(request.body.decode())

        scim_obj.from_dict(body)
        try:
            scim_obj.save()
        except db.utils.IntegrityError as e:
            raise IntegrityError(str(e))

        content = json.dumps(scim_obj.to_dict())
        response = HttpResponse(content=content,
                                content_type=SCIM_CONTENT_TYPE,
                                status=201)
        response['Location'] = scim_obj.location
        return response


class PutView(object):
    def put(self, request, uuid):
        try:
            obj = self.model_cls.objects.get(id=uuid)
        except ObjectDoesNotExist:
            raise NotFound(uuid)

        scim_obj = self.scim_adapter(obj, request=request)

        body = json.loads(request.body.decode())

        scim_obj.from_dict(body)
        scim_obj.save()

        content = json.dumps(scim_obj.to_dict())
        response = HttpResponse(content=content,
                                content_type=SCIM_CONTENT_TYPE)
        response['Location'] = scim_obj.location
        return response


class PatchView(object):
    def patch(self, request, uuid):

        try:
            obj = self.model_cls.objects.get(id=uuid)
        except ObjectDoesNotExist:
            raise NotFound(uuid)

        scim_obj = self.scim_adapter(obj, request=request)
        body = json.loads(request.body.decode())

        operations = body.get('Operations')

        with transaction.atomic():
            scim_obj.handle_operations(operations)

        content = json.dumps(scim_obj.to_dict())
        response = HttpResponse(content=content,
                                content_type=SCIM_CONTENT_TYPE)
        response['Location'] = scim_obj.location
        return response


class UsersView(FilterMixin, GetView, PostView, PutView, PatchView, DeleteView, SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    scim_adapter = get_user_adapter()
    model_cls = get_user_model()
    parser = SCIMUserFilterTransformer


class GroupsView(FilterMixin, GetView, PostView, PutView, PatchView, DeleteView, SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    scim_adapter = get_group_adapter()
    model_cls = get_group_model()
    parser = None


class ServiceProviderConfigView(SCIMView):
    http_method_names = ['get']

    def get(self, request):
        config = get_service_provider_config_model()(request=request)
        content = json.dumps(config.to_dict())
        return HttpResponse(content=content,
                            content_type=SCIM_CONTENT_TYPE)


class ResourceTypesView(SCIMView):

    http_method_names = ['get']

    def type_dict_by_type_id(self, request):
        type_adapters = get_user_adapter(), get_group_adapter()
        type_dicts = [m.resource_type_dict(request) for m in type_adapters]
        return {d['id']: d for d in type_dicts}

    def get(self, request, uuid=None, *args, **kwargs):
        if uuid:
            doc = self.type_dict_by_type_id(request).get(uuid)
            if not doc:
                return HttpResponse(content_type=SCIM_CONTENT_TYPE, status=404)

        else:
            key_func = lambda o: o.get('id')
            type_dicts = self.type_dict_by_type_id(request).values()
            types = list(sorted(type_dicts, key=key_func))
            doc = {
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
                'Resources': types,
            }

        return HttpResponse(content=json.dumps(doc),
                            content_type=SCIM_CONTENT_TYPE)


class SchemasView(SCIMView):

    http_method_names = ['get']

    schemas_by_uri = {s['id']: s for s in ALL_SCHEMAS}

    def get(self, request, uuid=None, *args, **kwargs):
        if uuid:
            doc = self.schemas_by_uri.get(uuid)
            if not doc:
                return HttpResponse(content_type=SCIM_CONTENT_TYPE, status=404)

        else:
            key_func = lambda o: o.get('id')
            schemas = list(sorted(self.schemas_by_uri.values(), key=key_func))
            doc = {
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
                'Resources': schemas,
            }

        content = json.dumps(doc)
        return HttpResponse(content=content,
                            content_type=SCIM_CONTENT_TYPE)

