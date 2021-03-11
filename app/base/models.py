import uuid

from django.db import models
from django_extensions.db.models import ActivatorModel, TimeStampedModel

from .managers import MFModelManager
# Create your models here.



class MFBaseModel(ActivatorModel, TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    objects = MFModelManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True



class APIBaseModel(MFBaseModel):

    class METHOD:
        GET    = 1
        POST   = 2
        PUT    = 3
        PATCH  = 4
        DELETE = 5

    METHOD_CHOICES = (
        (METHOD.GET, 'GET'),
        (METHOD.POST, 'POST'),
        (METHOD.PUT, 'PUT'),
        (METHOD.PATCH, 'PATCH'),
        (METHOD.DELETE, 'DELETE'),
    )

    class AUTH_SCHEME:
        API_KEY      = 1
        BEARER_TOKEN = 2

    AUTH_SCHEME_CHOICES = (
        (AUTH_SCHEME.API_KEY, 'API Key'),
        (AUTH_SCHEME.BEARER_TOKEN, 'Bearer Token')
    )
    
    name = models.CharField(max_length=255, verbose_name='API Name',
                        help_text='Name of the API')

    path = models.CharField(max_length=255, verbose_name='API Path')

    params = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Query Parameters')

    body = models.JSONField(null=True, blank=True, default=dict,
                        verbose_name='Request Body')

    method = models.PositiveSmallIntegerField(choices=METHOD_CHOICES)

    auth_scheme = models.PositiveSmallIntegerField(choices=AUTH_SCHEME_CHOICES,
                        verbose_name='Auth Scheme')

    priority = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True



class SystemBaseModel(MFBaseModel):
    base_url = models.URLField(max_length=255, null=True, blank=True,
                        verbose_name='API Base URL')
    api_key = models.CharField(max_length=255, null=True, blank=True,
                        verbose_name='API Key')
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    jwt_obtain = models.URLField(max_length=255, null=True, blank=True,
                        verbose_name='JWT Obtain URL')
    jwt_refresh = models.URLField(max_length=255, null=True, blank=True,
                        verbose_name='JWT Refresh URL')
    class Meta:
        abstract = True
