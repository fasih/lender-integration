import structlog as logging

from django.conf import settings
from django.http.response import Http404

from drf_yasg2 import openapi
from drf_yasg2.views import get_schema_view
from drf_yasg2.utils import swagger_auto_schema

from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import server_error
from rest_framework.views import exception_handler as _exception_handler

from . import description, title, version
from .exceptions import MFAPIException
from .schema import TagOpenAPISchemaGenerator

# Create your views here.



logger = logging.getLogger(__name__)



class MFAPIView(generics.GenericAPIView):
    model_class = None

    def get_view_name(self):
        view_name = super().get_view_name().replace(' ', '')
        return view_name

    def get_queryset(self):
    	if self.model_class:
    	    return self.model_class.objects.all()
    	return super().get_queryset()

    def initial(self, request, *args, **kwargs):
        log_data = dict(
            request_path = request.path,
            view_name = self.get_view_name(),
            request_data = getattr(request, 'data', {}),
            request_method = getattr(request, 'method', ''),
            **kwargs
        )
        logger.info('initial', **log_data)
        super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        log_data = dict(
            request_path = request.path,
            view_name = self.get_view_name(),
            request_data = getattr(request, 'data', {}),
            response_data = getattr(response, 'data', {}),
            request_method = getattr(request, 'method', ''),
            **kwargs
        )
        logger.info('finalize_response', **log_data)
        return response


SchemaView = get_schema_view(
    openapi.Info(
        title=title,
        default_version=version,
        description=description,
        license=openapi.License(name="BSD License"),
        contact=openapi.Contact(**settings.API_CONTACT),
        terms_of_service=settings.WEB_URL+"/terms-of-use/",
        x_logo={
            "href": settings.API_URL,
            "altText": settings.SITE_URL,
            "backgroundColor": settings.MATERIAL_ADMIN_SITE['MAIN_BG_COLOR'],
            "url": settings.SITE_URL + settings.STATIC_URL +
                    'material/admin/images/login-logo-default.jpg',
        },
    ),
    public=True,
    url=settings.API_URL,
    permission_classes=(permissions.AllowAny,),
    generator_class=TagOpenAPISchemaGenerator,
)


def exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    view = context.get('view')
    request = context.get('request')
    response = _exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if isinstance(exc, MFAPIException):
        response.data = exc.get_full_details()
    elif isinstance(exc, Http404):
        response.data = {
            'message': str(exc),
            'code': 404
        }

    logger.exception('exception_handler',
        view_name = view.get_view_name(),
        request_method=request.method,
        request_path=request.path,
        msg=str(exc),
    )
    return response or server_error(None)
