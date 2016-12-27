django-scim2
============

This is a partial provider-side implementation of the SCIM 2.0 [1]_
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

Add the necessary url patterns to your root urls.py file. Please note that the
namespace is mandatory and must be named `scim`::

    urlpatterns = [
        ...
        url(r'^scim/v2/', include('django_scim.urls', namespace='scim')),
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

Source
------

https://github.com/15five/django-scim2

Documentation
-------------

.. image:: https://readthedocs.org/projects/django-scim2/badge/?version=latest
  :target: http://django-scim2.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

http://django-scim2.readthedocs.io/

Tests
-----

.. image:: https://travis-ci.org/15five/django-scim2.svg?branch=master
   :target: https://travis-ci.org/15five/django-scim2

https://travis-ci.org/15five/django-scim2

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

Credits
-------

This project was forked from https://bitbucket.org/atlassian/django_scim


.. [1] http://www.simplecloud.info/, https://tools.ietf.org/html/rfc7644

