import stringcase

from django.db import models
from django.db.models.signals import post_save, pre_save

from base.models import *
# Create your models here.



class LoanManagementSystem(ServiceBaseModel):
    name = models.CharField(max_length=255, verbose_name='LMS',
                        help_text='Name of the Loan Management System')
    code = models.CharField(max_length=10, unique=True, verbose_name='LMS Code')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'LMS'
        verbose_name_plural = 'LMS'



class LoanManagementSystemAPI(APIBaseModel):
    lms = models.ForeignKey('platforms.LoanManagementSystem', null=True,
                            on_delete=models.SET_NULL, verbose_name='LMS')
    data = models.ManyToManyField('borrowers.LoanApplication',
                    through='borrowers.LoanApplicationData',
                    through_fields=('lms_api', 'app'))

    def __str__(self):
        return f'({self.lms}) - {self.name}'

    class Meta:
        verbose_name = 'LMS API'
        verbose_name_plural = 'LMS API'



class ChannelPartners(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Channel Partner',
                        help_text='Name of the Channel Partner')
    code = models.CharField(max_length=10, unique=True, help_text='Will be'
                                'prefixed with lmsId to generate loanId')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Channel Partner'
        verbose_name_plural = 'Channel Partners'



class PlatformService(ServiceBaseModel):
    name = models.CharField(max_length=255, verbose_name='Service',
                        help_text='Name of the platform service')
    code = models.CharField(max_length=10, unique=True, verbose_name='Service'
                                ' Code')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'



class PlatformServiceAPI(APIBaseModel):
    svc = models.ForeignKey('platforms.PlatformService', null=True,
                            on_delete=models.SET_NULL, verbose_name='SVC')
    data = models.ManyToManyField('borrowers.LoanApplication',
                    through='borrowers.LoanApplicationData',
                    through_fields=('svc_api', 'app'))

    def __str__(self):
        return f'({self.svc}) - {self.name}'

    class Meta:
        verbose_name = 'Service API'
        verbose_name_plural = 'Services API'



def lms_api_pre_save(sender, instance, **kwargs):
    instance.name = stringcase.alphanumcase(instance.name)

pre_save.connect(lms_api_pre_save, sender=LoanManagementSystemAPI)



def platform_service_api_pre_save(sender, instance, **kwargs):
    instance.name = stringcase.alphanumcase(instance.name)

pre_save.connect(platform_service_api_pre_save, sender=PlatformServiceAPI)
