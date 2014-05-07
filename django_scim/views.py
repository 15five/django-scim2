import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import six

from django_scim.filter import SCIMFilterTransformer
from django_scim.models import SCIMUser


class SCIMException(Exception):
    status = 500


class NotFound(SCIMException):
    status = 404


class BadRequest(SCIMException):
    status = 400


class SCIMView(View):
    usercls = SCIMUser

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


class UserView(SCIMView):
    http_method_names = ['get']

    def get(self, request, uuid):
        try:
            user = self.usercls(User.objects.get(id=uuid))
        except ObjectDoesNotExist as e:
            raise NotFound(e)
        else:
            return HttpResponse(json.dumps(user.to_dict(), encoding='utf-8'),
                                content_type='application/json; charset=utf-8')

class SearchView(SCIMView):
    parser = SCIMFilterTransformer

    def _page(self, request):
        try:
            start = request.GET.get('startIndex', 1)
            if start is not None:
                start = int(start)
                if start < 1:
                    raise BadRequest(
                        'Invalid startIndex (must be >= 1)')
            count = request.GET.get('count', 50)
            if count is not None:
                count = int(count)
            return start, count
        except ValueError as e:
            raise BadRequest('Invalid pagination values: ' + str(e))

    def _search(self, query, start, count):
        try:
            qs = self.parser.search(query)
            doc = {
                'totalResults': sum((1 for _ in qs)),
                'itemsPerPage': count,
                'startIndex': start,
                'schemas': ['urn:scim:schemas:core:2.0'],
                'Resources': [self.usercls(u).to_dict() for u
                              in qs[start-1:(start-1) + count]]
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
