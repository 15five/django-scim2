from django.conf import settings


def get_full_domain_from_request(request):
    domain = settings.MAIN_DOMAIN

    host = request.META.get('HTTP_X_FORWARDED_HOST', '')  # for proxy forwards
    if not host:
        host = request.META.get('HTTP_HOST', '')
    host_parts = host.split('.')

    subdomain = ''
    if len(host_parts) > 2:
        # all parts sans the domain, assumes main domain is a two part domain
        subdomain = '.'.join(host_parts[:-2])

    if subdomain:
        domain = subdomain + '.' + domain

    return '{scheme}{domain}'.format(
        scheme='https://' if request.is_secure() else 'http://',
        domain=domain,
    )


def get_extra_model_filter_kwargs_getter(model):
    """
    Return a function that will return extra model filter kwargs for the passed in model.

    :param model:
    """

    if getattr(model, '__name__', None) == 'User':

        def get_extra_filter_kwargs(self, request, *args, **kwargs):
            """
            Return extra filter kwargs for the given model.
            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {
                'company_id': request.user.company_id,
            }

    elif getattr(model, '__name__', None) == 'Group':

        def get_extra_filter_kwargs(self, request, *args, **kwargs):
            """
            Return extra filter kwargs for the given model.

            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {
                'company_id': request.user.company_id,
            }

    else:

        # For 'search' case
        def get_extra_filter_kwargs(self, request, *args, **kwargs):
            """
            Return extra filter kwargs for the given model.

            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {
                'company_id': request.user.company_id,
            }

    return get_extra_filter_kwargs


def get_extra_model_exclude_kwargs_getter(model):
    """
    Return a function that will return extra model exclude kwargs for the passed in model.

    :param model:
    """

    if getattr(model, '__name__', None) == 'User':

        def get_extra_exclude_kwargs(self, request, *args, **kwargs):
            """
            Return extra exclude kwargs for the given model.
            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {}

    elif getattr(model, '__name__', None) == 'Group':

        def get_extra_exclude_kwargs(self, request, *args, **kwargs):
            """
            Return extra exclude kwargs for the given model.

            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {}

    else:

        # For 'search' case
        def get_extra_exclude_kwargs(self, request, *args, **kwargs):
            """
            Return extra exclude kwargs for the given model.

            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {}

    return get_extra_exclude_kwargs
