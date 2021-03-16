from django.db import models

from base.models import *
from base.utils import *
# Create your models here.



class LoanApplication(BaseModel):
    lmsid = models.CharField(max_length=255, null=True,
                    verbose_name='Loan Application Reference No.',
                    help_text='LoanID at LMS')

    lms = models.ForeignKey('platforms.LoanManagementSystem', null=True,
                    on_delete=models.SET_NULL, verbose_name='LMS')

    lender = models.ForeignKey('lenders.LenderSystem', null=True,
                    on_delete=models.SET_NULL, verbose_name='Lender')

    cp = models.ForeignKey('platforms.ChannelPartners', null=True, blank=True,
                    on_delete=models.SET_NULL, verbose_name='Channel Partner')

    svc = models.ManyToManyField('platforms.PlatformService', blank=True,
                    verbose_name='Services')

    def __str__(self):
        return self.lmsid or '-'

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        unique_together = ('lms', 'lmsid')



class LoanApplicationData(BaseModel):
    app = models.ForeignKey('borrowers.LoanApplication', null=True,
                        on_delete=models.SET_NULL, verbose_name='Application')

    lms_api = models.ForeignKey('platforms.LoanManagementSystemAPI', null=True,
                        blank=True, on_delete=models.SET_NULL,
                        verbose_name='LMS API')

    svc_api = models.ForeignKey('platforms.PlatformServiceAPI', null=True,
                        blank=True, on_delete=models.SET_NULL,
                        verbose_name='SVC API')

    request = models.JSONField(null=True, default=dict, blank=True)
    response = models.JSONField(null=True, default=dict, blank=True)

    response_code = models.PositiveSmallIntegerField(null=True, blank=True,
                        verbose_name='Response Status Code')

    response_file = models.FileField(null=True, blank=True,
                                upload_to=file_uploads)

    def __str__(self):
        return self.app and self.app.lmsid or '-'

    class Meta:
        verbose_name = 'Application Data'
        verbose_name_plural = 'Applications Data'



