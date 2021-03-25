from django.db.utils import OperationalError

from lenders.models import LenderSystem
from platforms.models import (ChannelPartners, LoanManagementSystem,
    PlatformService
)



try:
    CP_CHOICES = ChannelPartners.objects.values_list('code', 'name')
    LENDER_CHOICES = LenderSystem.objects.values_list('code', 'name')
    LMS_CHOICES = LoanManagementSystem.objects.values_list('code', 'name')
    SVC_CHOICES = PlatformService.objects.values_list('code', 'name')
except:
    CP_CHOICES = []
    LENDER_CHOICES = []
    LMS_CHOICES = []
    SVC_CHOICES = []
