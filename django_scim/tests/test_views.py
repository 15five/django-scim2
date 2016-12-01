import json
from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.test import RequestFactory
from django.utils.six.moves.urllib.parse import urljoin

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from django_scim import views
from django_scim.utils import get_user_adapter
from django_scim.constants import BASE_SCIM_LOCATION
from django_scim.constants import BASE_URL


class SCIMTestCase(TestCase):
    maxDiff = None
    factory = RequestFactory()

    @skip('')
    def test_dispatch(self):
        self.fail('TODO')

    def test_status_501(self):
        request = self.factory.get('/noop')

        class Status501View(views.SCIMView):
            implemented = False

        resp = Status501View.as_view()(request)
        self.assertEqual(resp.status_code, 501)

    @skip('')
    def test_auth_request(self):
        self.fail('TODO')


class FilterMixinTestCase(TestCase):
    maxDiff = None
    factory = RequestFactory()

    def test__page(self):
        request = self.factory.get('/noop?startIndex=11&count=23')
        start, count = views.FilterMixin()._page(request)

        self.assertEqual(start, 11)
        self.assertEqual(count, 23)

    @skip('')
    def test__search(self):
        self.fail('TODO')

    def test__build_response(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
        )
        ford = get_user_adapter()(ford)
        abernathy = get_user_model().objects.create(
            first_name='Dolores',
            last_name='Abernathy',
            username='dabernathy',
        )
        abernathy = get_user_adapter()(abernathy)

        qs = get_user_model().objects.all()
        mixin = views.FilterMixin()
        mixin.scim_adapter = get_user_adapter()
        resp = mixin._build_response(qs, 1, 5)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 2,
            "itemsPerPage": 5,
            "startIndex": 1,
            'Resources': [
                ford.to_dict(),
                abernathy.to_dict(),
            ],
        }
        self.assertEqual(expected, result)


class SearchTestCase(TestCase):
    maxDiff = None

    def test_search_without_schema(self):
        """
        Test POST /Users/.search/?filter=userName eq ""
        """
        c = Client()
        url = reverse('scim:users-search')
        body = json.dumps({
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:NotSearchRequest'],
        })
        resp = c.post(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 400, resp.content)

        result = json.loads(resp.content)
        expected = {
            'detail': u'Invalid schema uri. Must be SearchRequest.',
            'schemas': [u'urn:ietf:params:scim:api:messages:2.0:Error'],
            'status': 400
        }
        self.assertEqual(expected, result)

    def test_search_for_user_with_username_filter(self):
        """
        Test POST /Users/.search/?filter=userName eq ""
        """
        c = Client()
        url = reverse('scim:users-search')
        body = json.dumps({
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:SearchRequest'],
            'filter': 'userName eq ""',
        })
        resp = c.post(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)
        location = urljoin(BASE_SCIM_LOCATION, BASE_URL)
        location = urljoin(location, 'Users/.search')
        self.assertEqual(resp['Location'], location)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 0,
            "itemsPerPage": 50,
            "startIndex": 1,
            "Resources": [],
        }
        self.assertEqual(expected, result)


class UserTestCase(TestCase):
    maxDiff = None

    def test_get_user_with_username_filter(self):
        """
        Test GET /Users?filter=userName eq ""
        """
        c = Client()
        url = reverse('scim:users') + '?filter=userName eq ""'
        resp = c.get(url, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 0,
            "itemsPerPage": 50,
            "startIndex": 1,
            "Resources": [],
        }
        self.assertEqual(expected, result)

    def test_get_user_by_id(self):
        """
        Test GET /Users/{id}
        """
        # create user
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford'
        )
        ford = get_user_adapter()(ford)

        c = Client()
        url = reverse('scim:users', kwargs={'uuid': ford.id})
        resp = c.get(url, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp['Location'], ford.location)

        result = json.loads(resp.content)
        expected = ford.to_dict()
        self.assertEqual(expected, result)

    def test_get_all_users(self):
        """
        Test GET /Users
        """
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
        )
        ford = get_user_adapter()(ford)
        abernathy = get_user_model().objects.create(
            first_name='Dolores',
            last_name='Abernathy',
            username='dabernathy',
        )
        abernathy = get_user_adapter()(abernathy)

        c = Client()
        url = reverse('scim:users')
        resp = c.get(url, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        result = json.loads(resp.content)
        expected = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 2,
            "itemsPerPage": 50,
            "startIndex": 1,
            'Resources': [
                ford.to_dict(),
                abernathy.to_dict(),
            ],
        }
        self.assertEqual(expected, result)

    def test_post(self):
        c = Client()
        url = reverse('scim:users')
        data = {
            'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
            'userName': 'ehughes',
            'name': {
                'givenName': 'Elsie',
                'familyName': 'Hughes',
            },
            'password': 'notTooSecret',
            'emails': [{'value': 'ehughes@westworld.com', 'primary': True}],
        }
        body = json.dumps(data)
        resp = c.post(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 201, resp.content)

        # test object
        elsie = get_user_model().objects.get(username='ehughes')
        self.assertEqual(elsie.first_name, 'Elsie')
        self.assertEqual(elsie.last_name, 'Hughes')
        self.assertEqual(elsie.email, 'ehughes@westworld.com')

        # test response
        elsie = get_user_adapter()(elsie)
        result = json.loads(resp.content)
        self.assertEqual(result, elsie.to_dict())
        self.assertEqual(resp['Location'], elsie.location)

    def test_put(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )

        c = Client()
        url = reverse('scim:users', kwargs={'uuid': ford.id})
        data = get_user_adapter()(ford).to_dict()
        data['userName'] = 'updatedrford'
        data['name'] = {'givenName': 'Bobby'}
        data['emails'] = [{'value': 'rford@westworld.com', 'primary': True}]
        body = json.dumps(data)
        resp = c.put(url, body, content_type='application/scim+json')
        self.assertEqual(resp.status_code, 200, resp.content)

        # test object
        ford.refresh_from_db()
        self.assertEqual(ford.first_name, 'Bobby')
        self.assertEqual(ford.last_name, '')
        self.assertEqual(ford.username, 'updatedrford')
        self.assertEqual(ford.email, 'rford@westworld.com')

        # test response
        result = json.loads(resp.content)
        ford = get_user_adapter()(ford)
        self.assertEqual(result, ford.to_dict())

    @skip('')
    def test_patch(self):
        self.fail('TODO')

    def test_delete(self):
        ford = get_user_model().objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )

        c = Client()
        url = reverse('scim:users', kwargs={'uuid': ford.id})
        resp = c.delete(url)
        self.assertEqual(resp.status_code, 204, resp.content)

        ford = get_user_model().objects.filter(id=ford.id).first()
        self.assertIsNone(ford)


class GroupTestCase(TestCase):
    maxDiff = None

    def test_get(self):
        self.fail('TODO')

    def test_post(self):
        self.fail('TODO')

    def test_put(self):
        self.fail('TODO')

    def test_patch(self):
        self.fail('TODO')

    def test_delete(self):
        self.fail('TODO')


class ServiceProviderConfigTestCase(TestCase):
    maxDiff = None

    def test_get(self):
        self.fail('TODO')


class ResourceTypesTestCase(TestCase):
    maxDiff = None

    def test_get(self):
        self.fail('TODO')


class SchemasTestCase(TestCase):
    maxDiff = None

    def test_get(self):
        self.fail('TODO')

