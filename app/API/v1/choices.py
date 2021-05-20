from enum import Enum

from django.db import models

from lenders.models import LenderSystem
from platforms.models import (ChannelPartners, LoanManagementSystem,
    PlatformService)



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



class TASK_STATUS(models.TextChoices):
    SUBMITTED = 'SUBMITTED'
    RUNNING = 'RUNNING'



class WORKFLOW_STATUS(models.TextChoices):
    FAILED = 'FAILED'
    FETCHED = 'FETCHED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    NOT_COMPLETED = 'NOT COMPLETED'
