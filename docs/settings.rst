Settings
========

USER_ADAPTER
    Default: 'django_scim.adapters.SCIMUser'

GROUP_MODEL
    Default: 'django.contrib.auth.models.Group'

GROUP_ADAPTER
    Default: 'django_scim.adapters.SCIMGroup'

USER_FILTER_PARSER
    Default: 'django_scim.filters.UserFilterQuery'

GROUP_FILTER_PARSER
    Default: 'django_scim.filters.GroupFilterQuery'

SERVICE_PROVIDER_CONFIG_MODEL
    Default: 'django_scim.models.SCIMServiceProviderConfig'

BASE_LOCATION_GETTER
    Default: 'django_scim.utils.default_base_scim_location_getter'

GET_EXTRA_MODEL_FILTER_KWARGS_GETTER
    Default: 'django_scim.utils.default_get_extra_model_filter_kwargs_getter'

GET_EXTRA_MODEL_EXCLUDE_KWARGS_GETTER
    Default: 'django_scim.utils.default_get_extra_model_exclude_kwargs_getter'

GET_OBJECT_POST_PROCESSOR_GETTER
    Default: 'django_scim.utils.default_get_object_post_processor_getter'

GET_QUERYSET_POST_PROCESSOR_GETTER
    Default: 'django_scim.utils.default_get_queryset_post_processor_getter'

SCHEMAS_GETTER
    Default: 'django_scim.schemas.default_schemas_getter'

DOCUMENTATION_URI
    Default: None

SCHEME
    Default: 'https'

NETLOC
    Default: None

EXPOSE_SCIM_EXCEPTIONS
    Default: False

    In some circumstances it can be beneficial for the client
    to know what caused an error. However, this can present an
    unacceptable security risk for many companies. This flag
    allows for a generic error message to be returned when such a
    security risk is unacceptable.

AUTHENTICATION_SCHEMES
    Default: []

WWW_AUTHENTICATE_HEADER
    Default: 'Basic realm="django-scim2"'
