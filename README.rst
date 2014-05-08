Django SCIM
===========

This is a partial provider-side implementation of the SCIM 2.0 [1]_
specification for use in Django. It covers:

- Serialization of Django ``User`` objects to SCIM documents
- REST view for ``<prefix>/Users/uid``
- REST view for ``<prefix>/Users/.search``
- SCIM filter query parser covering all operators and most fields
- Limited pluggability support

Note that currently the only supported database is Postgres.


Installation
------------

::

    $ pip install django_scim

Then add the ``django_scim`` app to ``INSTALLED_APPS`` in Django's settings
file and the necessary url mappings::

    urlpatterns = patterns('',
        url(r'^/scim/v2/Users/.search/?$',
            SearchView.as_view(), name='scim-search'),
        url(r'^/scim/v2/Users/([^/]+)$', UserView.as_view(), name='scim-user'),
    )


Extensibility
-------------

By default, ``django_scim`` uses the email field on the ``User`` class. However,
if your application maintains multiple identities using custom separate
database tables, you can override ``django_scim.models.SCIMUser`` and pull that
in::

    from django_scim.models import SCIMUser as _SCIMUser

    from acme.apps.bb.models import Identity


    class SCIMUser(_SCIMUser):
        def __init__(self, user):
            super(SCIMUser, self).__init__(user)
            self.identities = (Identity.objects
                                       .filter(profile__user_id=self.user.id))

        @property
        def emails(self):
            return {i.email: i.primary for i in self.identities}


Here we keep multiple email addresses in a table that is linked to
``UserProfile``. Next, tell the views to use this class instead of the
default::

        url(r'^/scim/v2/Users/([^/]+)$', UserView.as_view(usercls=SCIMUser),
            name='scim-user'),

When your email address live in different tables, you'll also need to extend
the filter query parser to make sure they can be queried on::

    from django_scim.filter import SCIMFilterTransformer


    class AcmeSCIMTransformer(SCIMFilterTransformer):
        email = lambda *args: 'i.email'

        def join(self):
            return """
                JOIN bb_userprofile p ON p.user_id = u.id
                LEFT OUTER JOIN bb_identity i ON i.profile_id = p.id
                """

And pass it on to the view::

        url(r'^/scim/v2/Users/([^/]+)$',
            UserView.as_view(usercls=SCIMUser, parser=AcmeSCIMTransformer),
            name='scim-user'),


.. [1] http://www.simplecloud.info/
