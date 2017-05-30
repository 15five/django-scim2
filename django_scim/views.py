import json
import logging

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

from . import constants
from .filters import SCIMUserFilterTransformer
from .exceptions import SCIMException
from .exceptions import NotFoundError
from .exceptions import BadRequestError
from .exceptions import IntegrityError
from .utils import get_all_schemas_getter
from .utils import get_group_adapter
from .utils import get_group_model
from .utils import get_user_adapter
from .utils import get_base_scim_location_getter
from .utils import get_service_provider_config_model
from .utils import get_extra_model_filter_kwargs_getter


logger = logging.getLogger(__name__)


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
            logger.exception('Unable to complete SCIM call.')
            if not isinstance(e, SCIMException):
                e = SCIMException(six.text_type(e))

            content = json.dumps(e.to_dict())
            return HttpResponse(content=content,
                                content_type=constants.SCIM_CONTENT_TYPE,
                                status=e.status)

    def status_501(self, request, *args, **kwargs):
        """
        A service provider that does NOT support a feature SHOULD
        respond with HTTP status code 501 (Not Implemented).
        """
        return HttpResponse(content_type=constants.SCIM_CONTENT_TYPE, status=501)


class FilterMixin(object):

    parser = None
    scim_adapter = None

    def _page(self, request):
        try:
            start = request.GET.get('startIndex', 1)
            if start is not None:
                start = int(start)
                if start < 1:
                    raise BadRequestError('Invalid startIndex (must be >= 1)')

            count = request.GET.get('count', 50)
            if count is not None:
                count = int(count)

            return start, count

        except ValueError as e:
            raise BadRequestError('Invalid pagination values: ' + str(e))

    def _search(self, request, query, start, count):
        try:
            qs = self.parser.search(query, request)
        except ValueError as e:
            raise BadRequestError('Invalid filter/search query: ' + str(e))

        extra_filter_kwargs = self.get_extra_filter_kwargs(request)
        qs = self._filter_raw_queryset_with_extra_filter_kwargs(qs, extra_filter_kwargs)

        return self._build_response(request, qs, start, count)

    def _filter_raw_queryset_with_extra_filter_kwargs(self, qs, extra_filter_kwargs):

        obj_list = []
        for obj in qs:
            add_obj = True
            for attr_name, attr_val in extra_filter_kwargs.items():
                if not hasattr(obj, attr_name) or getattr(obj, attr_name, None) != attr_val:
                    add_obj = False
                    break

            obj_list.append(obj)

        return obj_list

    def _build_response(self, request, qs, start, count):
        try:
            total_count = sum(1 for _ in qs)
            qs = qs[start-1:(start-1) + count]
            resources = [self.scim_adapter(o, request=request).to_dict() for o in qs]
            doc = {
                'schemas': [constants.SchemaURI.LIST_RESPONSE],
                'totalResults': total_count,
                'itemsPerPage': count,
                'startIndex': start,
                'Resources': resources,
            }
        except ValueError as e:
            raise BadRequestError(six.text_type(e))
        else:
            content = json.dumps(doc)
            return HttpResponse(content=content,
                                content_type=constants.SCIM_CONTENT_TYPE)


class SearchView(FilterMixin, SCIMView):
    http_method_names = ['post']

    scim_adapter = None
    get_extra_filter_kwargs = get_extra_model_filter_kwargs_getter('search')

    def post(self, request):
        body = json.loads(request.body.decode() or '{}')
        if body.get('schemas') != [constants.SchemaURI.SERACH_REQUEST]:
            raise BadRequestError('Invalid schema uri. Must be SearchRequest.')

        query = body.get('filter', request.GET.get('filter'))

        if not query:
            raise BadRequestError('No filter query specified')
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

        extra_filter_kwargs = self.get_extra_filter_kwargs(request, uuid)
        extra_filter_kwargs['id'] = uuid  # Override ID with passed UUID

        try:
            obj = self.model_cls.objects.get(**extra_filter_kwargs)
        except ObjectDoesNotExist as _e:
            raise NotFoundError(uuid)
        else:
            scim_obj = self.scim_adapter(obj, request=request)
            content = json.dumps(scim_obj.to_dict())
            response = HttpResponse(content=content,
                                    content_type=constants.SCIM_CONTENT_TYPE)
            response['Location'] = scim_obj.location
            return response

    def get_many(self, request):
        query = request.GET.get('filter')
        if query:
            return self._search(request, query, *self._page(request))

        extra_filter_kwargs = self.get_extra_filter_kwargs(request)
        qs = self.model_cls.objects.filter(**extra_filter_kwargs).order_by('id')
        return self._build_response(request, qs, *self._page(request))


class DeleteView(object):
    def delete(self, request, uuid):

        extra_filter_kwargs = self.get_extra_filter_kwargs(request, uuid)
        extra_filter_kwargs['id'] = uuid  # Override ID with passed UUID

        try:
            obj = self.model_cls.objects.get(**extra_filter_kwargs)
        except ObjectDoesNotExist as _e:
            raise NotFoundError(uuid)

        scim_obj = self.scim_adapter(obj, request=request)

        scim_obj.delete()

        return HttpResponse(status=204)


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
                                content_type=constants.SCIM_CONTENT_TYPE,
                                status=201)
        response['Location'] = scim_obj.location
        return response


class PutView(object):
    def put(self, request, uuid):

        extra_filter_kwargs = self.get_extra_filter_kwargs(request, uuid)
        extra_filter_kwargs['id'] = uuid  # Override ID with passed UUID

        try:
            obj = self.model_cls.objects.get(**extra_filter_kwargs)
        except ObjectDoesNotExist:
            raise NotFoundError(uuid)

        scim_obj = self.scim_adapter(obj, request=request)

        body = json.loads(request.body.decode())

        scim_obj.from_dict(body)
        scim_obj.save()

        content = json.dumps(scim_obj.to_dict())
        response = HttpResponse(content=content,
                                content_type=constants.SCIM_CONTENT_TYPE)
        response['Location'] = scim_obj.location
        return response


class PatchView(object):
    def patch(self, request, uuid):

        extra_filter_kwargs = self.get_extra_filter_kwargs(request, uuid)
        extra_filter_kwargs['id'] = uuid  # Override ID with passed UUID

        try:
            obj = self.model_cls.objects.get(**extra_filter_kwargs)
        except ObjectDoesNotExist:
            raise NotFoundError(uuid)

        scim_obj = self.scim_adapter(obj, request=request)
        body = json.loads(request.body.decode())

        operations = body.get('Operations')

        with transaction.atomic():
            scim_obj.handle_operations(operations)

        content = json.dumps(scim_obj.to_dict())
        response = HttpResponse(content=content,
                                content_type=constants.SCIM_CONTENT_TYPE)
        response['Location'] = scim_obj.location
        return response


class UsersView(FilterMixin, GetView, PostView, PutView, PatchView, DeleteView, SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    scim_adapter = get_user_adapter()
    model_cls = get_user_model()
    get_extra_filter_kwargs = get_extra_model_filter_kwargs_getter(model_cls)
    parser = SCIMUserFilterTransformer


class GroupsView(FilterMixin, GetView, PostView, PutView, PatchView, DeleteView, SCIMView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    scim_adapter = get_group_adapter()
    model_cls = get_group_model()
    get_extra_filter_kwargs = get_extra_model_filter_kwargs_getter(model_cls)
    parser = None


class ServiceProviderConfigView(SCIMView):
    http_method_names = ['get']

    def get(self, request):
        config = get_service_provider_config_model()(request=request)
        content = json.dumps(config.to_dict())
        return HttpResponse(content=content,
                            content_type=constants.SCIM_CONTENT_TYPE)


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
                return HttpResponse(content_type=constants.SCIM_CONTENT_TYPE, status=404)

        else:
            key_func = lambda o: o.get('id')
            type_dicts = self.type_dict_by_type_id(request).values()
            types = list(sorted(type_dicts, key=key_func))
            doc = {
                'schemas': [constants.SchemaURI.LIST_RESPONSE],
                'Resources': types,
            }

        return HttpResponse(content=json.dumps(doc),
                            content_type=constants.SCIM_CONTENT_TYPE)


class SchemasView(SCIMView):

    http_method_names = ['get']

    schemas_by_uri = {s['id']: s for s in get_all_schemas_getter()()}

    def get(self, request, uuid=None, *args, **kwargs):
        if uuid:
            doc = self.schemas_by_uri.get(uuid)
            if not doc:
                return HttpResponse(content_type=constants.SCIM_CONTENT_TYPE, status=404)

        else:
            key_func = lambda o: o.get('id')
            schemas = list(sorted(self.schemas_by_uri.values(), key=key_func))
            doc = {
                'schemas': [constants.SchemaURI.LIST_RESPONSE],
                'Resources': schemas,
            }

        content = json.dumps(doc)
        return HttpResponse(content=content,
                            content_type=constants.SCIM_CONTENT_TYPE)

