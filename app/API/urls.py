from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView

from .views import *


urlpatterns = [
    path('v1/', include('API.v1.urls')),
]

urlpatterns += [
    #re_path(r'^swagger(?P<format>\.json|\.yaml)$', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger\.(?P<format>json|yaml)$', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-ui'),    
    path('', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('rest_framework.urls', namespace="drf")),
]
