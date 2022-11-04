django-scim2
============

|tests| |coverage| |docs|

This is a provider-side implementation of the SCIM 2.0 [1]_
specification for use in Django.

Note that currently the only supported database is Postgres.


Installation
------------

Install with pip::

$ pip install django-scim2

Then add the ``django_scim`` app to ``INSTALLED_APPS`` in your Django's settings::

    INSTALLED_APPS = (
        ...
        'django_scim',
    )

By default, ``request.user.is_anonymous()`` is checked to determine if the SCIM
request should be allowed or denied.

If you have specific authentication needs, look into overriding the default "is
authenticated predicate" (i.e. see ``GET_IS_AUTHENTICATED_PREDICATE`` for
details) or subclassing the middleware that performs the check
(``AUTH_CHECK_MIDDLEWARE``).

Add the necessary url patterns to your root urls.py file. Please note that the
namespace is mandatory and must be named `scim`::

    urlpatterns = [
        ...
        path('scim/v2/', include('django_scim.urls')),
    ]

Finally, add settings appropriate for you app to your settings.py file::

    SCIM_SERVICE_PROVIDER = {
        'NETLOC': 'localhost',
        'AUTHENTICATION_SCHEMES': [
            {
                'type': 'oauth2',
                'name': 'OAuth 2',
                'description': 'Oauth 2 implemented with bearer token',
            },
        ],
    }

Other SCIM settings can be provided but those listed above are required.

PyPI
----

https://pypi.python.org/pypi/django-scim2

Source
------

https://github.com/15five/django-scim2

Documentation
-------------

.. |docs| image:: https://readthedocs.org/projects/django-scim2/badge/
  :target: https://django-scim2.readthedocs.io/
  :alt: Documentation Status

https://django-scim2.readthedocs.io/

Development
-----------

This project uses Poetry to manage dependencies, etc. Thus to install the
necessary tools when developing, run:

```
poetry install
```

Tests
-----

.. |tests| image:: https://github.com/15five/django-scim2/workflows/CI%2FCD/badge.svg
    :target: https://github.com/15five/django-scim2/actions

https://github.com/15five/django-scim2/actions

Tests are typically run locally with `tox` (https://tox.wiki/). Tox will test
all supported versions of Python and Django.

```
tox
```

To run the test suite with a single version of Python (the version you created
the virtualenv with), run:


```
poetry run pytest tests/
```


Coverage
--------

.. |coverage| image:: https://codecov.io/gh/15five/django-scim2/graph/badge.svg
    :target: https://codecov.io/gh/15five/django-scim2

https://codecov.io/gh/15five/django-scim2/

```
tox -e coverage
```

License
-------

This library is released under the terms of the **MIT license**. Full details in ``LICENSE.txt`` file.


Extensibility
-------------

This library was forked and developed to be highly extensible. A number of
adapters can be defined to control what different endpoints do to your resources.
Please see the documentation for more details.

PLEASE NOTE: This app does not implement authorization and authentication.
Such tasks are left for other apps such as `Django OAuth Toolkit`_ to implement.

.. _`Django OAuth Toolkit`: https://github.com/evonove/django-oauth-toolkit

Development Speed
-----------------

Since this project is relatively stable, time is only dedicated to it on
Fridays. Thus if you issue a PR, bug, etc, please note that it may take a week
before we get back to you. Thanks you for your patience.

Credits
-------

This project was forked from https://bitbucket.org/atlassian/django_scim


.. [1] http://www.simplecloud.info/, https://tools.ietf.org/html/rfc7644
