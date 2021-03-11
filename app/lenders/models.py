from django.db import models

from base.models import *
# Create your models here.



class LenderSystem(SystemBaseModel):
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
                            on_delete=models.SET_NULL)
    data = models.ManyToManyField('borrowers.LoanApplication',
                through='lenders.LoanData',
                through_fields=('lender_api', 'app'))

    def __str__(self):
        return f'({self.lender}) - {self.name}'

    class Meta:
        verbose_name = 'Lender API'
        verbose_name_plural = 'Lender APIs'



class Loan(MFBaseModel):
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



class LoanData(MFBaseModel):
    loan = models.ForeignKey('lenders.Loan', null=True,
                        on_delete=models.SET_NULL)
    app = models.ForeignKey('borrowers.LoanApplication', null=True,
                        on_delete=models.SET_NULL)
    lender_api = models.ForeignKey('lenders.LenderSystemAPI', null=True,
                        on_delete=models.SET_NULL)
    request = models.JSONField(null=True, default=dict)
    response = models.JSONField(null=True, default=dict)



