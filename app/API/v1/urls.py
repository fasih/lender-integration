from django.urls import include, path, re_path

from .views import *


urlpatterns = [
    path('loans/', LoanApplicationCreateAPIView.as_view(), name='loan-create'),
    path('loans/<uuid:application_id>', LoanApplicationAPIView.as_view(), name='loan-retrive-update'),
]

