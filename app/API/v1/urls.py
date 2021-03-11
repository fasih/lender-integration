from django.urls import include, path, re_path

from .views import *


urlpatterns = [
    path('loans/', LoanCreateAPIView.as_view(), name='loan-create'),
    path('loans/<uuid:application_id>', LoanStatusAPIView.as_view(), name='loan-retrive'),
]

