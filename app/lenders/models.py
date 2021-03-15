import stringcase

from django.db import models
from django.db.models.signals import post_save, pre_save

from base.models import *
# Create your models here.



class LenderSystem(ServiceBaseModel):
    name = models.CharField(max_length=255, verbose_name='Lender',
                        help_text='Name of the Lender')
    code = models.CharField(max_length=10, unique=True, verbose_name='Lender Code')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Lender'
        verbose_name_plural = 'Lenders'



class LenderSystemAPI(APIBaseModel):
    lender = models.ForeignKey('lenders.LenderSystem', null=True,
                            on_delete=models.SET_NULL, verbose_name='Lender')
    data = models.ManyToManyField('borrowers.LoanApplication',
                    through='lenders.LoanData',
                    through_fields=('lender_api', 'app'))

    def __str__(self):
        return f'({self.lender}) - {self.name}'

    class Meta:
        verbose_name = 'Lender API'
        verbose_name_plural = 'Lenders API'



class Loan(BaseModel):
    app = models.ForeignKey('borrowers.LoanApplication', null=True,
                    on_delete=models.SET_NULL, verbose_name='Application')
    lender = models.ForeignKey('lenders.LenderSystem', null=True,
                            on_delete=models.SET_NULL)
    loanid = models.CharField(max_length=255, null=True,
                    verbose_name='Loan Reference No.', help_text='Lender LoanID')

    def __str__(self):
        return self.app and self.app.lmsid

    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        unique_together = ('lender', 'loanid')



class LoanData(BaseModel):
    loan = models.ForeignKey('lenders.Loan', null=True,
                        on_delete=models.SET_NULL)

    app = models.ForeignKey('borrowers.LoanApplication', null=True,
                        on_delete=models.SET_NULL, verbose_name='Application')

    lender_api = models.ForeignKey('lenders.LenderSystemAPI', null=True,
                        on_delete=models.SET_NULL, verbose_name='Lender API')

    request = models.JSONField(null=True, default=dict, blank=True)
    response = models.JSONField(null=True, default=dict, blank=True)
    response_code = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.app and self.app.lmsid or ''

    class Meta:
        verbose_name = 'Loan Data'
        verbose_name_plural = 'Loans Data'



def loandata_pre_save(sender, instance, **kwargs):
    instance.app = instance.app or instance.loan and instance.loan.app

pre_save.connect(loandata_pre_save, sender=LoanData)



def lender_system_api_pre_save(sender, instance, **kwargs):
    instance.name = stringcase.alphanumcase(instance.name)

pre_save.connect(lender_system_api_pre_save, sender=LenderSystemAPI)
