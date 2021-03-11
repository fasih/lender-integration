from django.db import models

from base.models import *
# Create your models here.



class LoanApplication(MFBaseModel):
    lms = models.ForeignKey('platforms.LoanManagementSystem', null=True,
                    on_delete=models.SET_NULL, verbose_name='LMS')
    cp = models.ForeignKey('platforms.ChannelPartners', null=True, blank=True,
                    on_delete=models.SET_NULL, verbose_name='Channel Partner')
    lmsid = models.CharField(max_length=255, null=True,
                    verbose_name='Loan Application Reference No.',
                    help_text='LoanID at LMS')

    def __str__(self):
        return self.lmsid

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        unique_together = ('lms', 'lmsid')



class LoanApplicationData(MFBaseModel):
    loan = models.ForeignKey('borrowers.LoanApplication', null=True,
                        on_delete=models.SET_NULL, verbose_name='Application')
    lms_api = models.ForeignKey('platforms.LoanManagementSystemAPI', null=True,
                        on_delete=models.SET_NULL, verbose_name='LMS API')
    request = models.JSONField(null=True, default=dict)
    response = models.JSONField(null=True, default=dict)

    def __str__(self):
        return self.loan and self.loan.lmsid

    class Meta:
        verbose_name = 'Application Data'
        verbose_name_plural = 'Application Data'



