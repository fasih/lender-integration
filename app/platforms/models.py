from django.db import models

from base.models import *
# Create your models here.



class LoanManagementSystem(SystemBaseModel):
    name = models.CharField(max_length=255, verbose_name='LMS',
                        help_text='Name of Loan Management System')
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
        verbose_name_plural = 'LMS APIs'



class ChannelPartners(MFBaseModel):
    name = models.CharField(max_length=255, verbose_name='Channel Partner',
                        help_text='Name of the Channel Partner')
    code = models.CharField(max_length=10, unique=True, help_text='Will be'
                                'prefixed with lmsId to generate loanId')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Channel Partner'
        verbose_name_plural = 'Channel Partners'



