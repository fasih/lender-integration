import uuid

from django.db import models
from django.db.models import Q
from django_extensions.db.models import ActivatorModel, TimeStampedModel

from .managers import MFModelManager
# Create your models here.



is_success = Q(response_code__gte=200) & Q(response_code__lte=299)



class BaseModel(ActivatorModel, TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    objects = MFModelManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True



class APIBaseModel(BaseModel):

    class METHOD:
        GET    = 'GET'
        PUT    = 'PUT'
        POST   = 'POST'
        PATCH  = 'PATCH'
        DELETE = 'DELETE'

    METHOD_CHOICES = (
        (METHOD.GET, 'GET'),
        (METHOD.PUT, 'PUT'),
        (METHOD.POST, 'POST'),
        (METHOD.PATCH, 'PATCH'),
        (METHOD.DELETE, 'DELETE'),
    )

    class AUTH_SCHEME:
        TOKEN  = 'Token'
        BEARER = 'Bearer'
        BASIC  = 'Basic'
        

    AUTH_SCHEME_CHOICES = (
        (AUTH_SCHEME.TOKEN, 'Token'),
        (AUTH_SCHEME.BEARER, 'Bearer'),
        (AUTH_SCHEME.BASIC, 'Basic'),
    )
    
    name = models.CharField(max_length=255, verbose_name='API Name',
                        help_text='Name of the API')

    path = models.CharField(max_length=255, verbose_name='API Path')

    params = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Query Parameters')

    headers = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Request Headers')

    body = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Request Body')

    iterable = models.BooleanField(null=True, blank=True, default=False,
                        help_text='Yes if the API is going to be called \
                            multiple times then also configure Iterable Data \
                            Settings')

    iterable_data = models.TextField(null=True, blank=True,
                        verbose_name='Iterable Data Path')

    iterable_filters = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Iterable Data Filters')

    method = models.CharField(max_length=10, choices=METHOD_CHOICES,
                        verbose_name='HTTP Method')

    auth_scheme = models.CharField(max_length=10, choices=AUTH_SCHEME_CHOICES,
                        verbose_name='HTTP Auth Scheme')

    priority = models.PositiveSmallIntegerField(null=True, blank=True,
                        verbose_name='Workflow Priority')

    class Meta:
        abstract = True



class ServiceBaseModel(BaseModel):
    base_url = models.URLField(max_length=255, null=True, blank=True,
                        verbose_name='API Base URL')

    api_key = models.TextField(null=True, blank=True, verbose_name='API Key')
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    params = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Query Parameters')

    headers = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Request Headers')

    body = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Request Body')

    oauth_url = models.URLField(max_length=500, null=True, blank=True,
                        verbose_name='OAuth URL')

    oauth_headers = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='OAuth Request Headers')

    oauth_body = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='OAuth Request Body')

    class Meta:
        abstract = True
