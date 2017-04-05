import six

from .settings import scim_settings


def get_user_adapter():
    """
    Return the user model adapter.
    """
    return scim_settings.USER_ADAPTER


def get_group_model():
    """
    Return the group model.
    """
    return scim_settings.GROUP_MODEL


def get_group_adapter():
    """
    Return the group model adapter.
    """
    return scim_settings.GROUP_ADAPTER


def get_service_provider_config_model():
    """
    Return the Service Provider Config model.
    """
    return scim_settings.SERVICE_PROVIDER_CONFIG_MODEL


def get_base_scim_location_getter():
    """
    Return a function that will, when called, returns the base
    location of scim app.
    """
    return scim_settings.BASE_LOCATION_GETTER


def get_all_schemas_getter():
    """
    Return a function that will, when called, returns the base
    location of scim app.
    """
    return scim_settings.SCHEMAS_GETTER


def get_extra_model_filter_kwargs_getter(model):
    """
    Return a function that will, when called, returns the base
    location of scim app.
    """
    return scim_settings.GET_EXTRA_MODEL_FILTER_KWARGS_GETTER(model)


def default_base_scim_location_getter(request=None, *args, **kwargs):
    """
    Return the default location of the app implementing the SCIM api.
    """
    base_scim_location_parts = (
        scim_settings.SCHEME,
        scim_settings.NETLOC,
        '',  # path
        '',  # params
        '',  # query
        ''   # fragment
    )

    base_scim_location = six.moves.urllib.parse.urlunparse(base_scim_location_parts)

    return base_scim_location


def default_get_extra_model_filter_kwargs_getter(model):
    """
    Return a **method** that will return extra model filter kwargs for the passed in model.

    :param model:  
    """
    def get_extra_filter_kwargs(self, request, *args, **kwargs):
        """
        Return extra filter kwargs for the given model.
        :param request: 
        :param args: 
        :param kwargs: 
        :rtype: dict 
        """
        return {}

    return get_extra_filter_kwargs
