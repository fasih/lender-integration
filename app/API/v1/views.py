import structlog as logging

from django.db.utils import IntegrityError

from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from drf_yasg2.utils import swagger_auto_schema

from .serializers import *
from .execptions import *

from API.views import MFAPIView
from lenders.models import *
from platforms.models import *



class LoanCreateAPIView(generics.CreateAPIView, MFAPIView):
    serializer_class = LoanApplicationRequestSerializer

    @swagger_auto_schema(responses={201: LoanApplicationResponseSerializer()})
    def post(self, request, *args, **kwargs):
        """Loan Application Create API

        API fetches borrowers loan application from LMS and create loan
        application at lenders side
        """        

        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        loan_application = LoanApplicationResponseSerializer(app)
        return Response(loan_application.data, status=status.HTTP_201_CREATED,
                            headers=headers)

    def perform_create(self, serializer):
        lms = generics.get_object_or_404(LoanManagementSystem.objects,
                    code=serializer.data['lms_code'])
        lender = generics.get_object_or_404(LenderSystem.objects,
                    code=serializer.data['lender_code'])
        if serializer.data.get('partner_code'):
            cp = generics.get_object_or_404(ChannelPartners.objects,
                        code=serializer.data['partner_code'])
        else:
            cp = None

        application = LoanApplication(lmsid=serializer.data['lmsid'], lms=lms,
                                lender=lender, cp=cp)
        try:
            application.save()
        except IntegrityError:
            raise LoanApplicationAlreadyExist()
        return application



class LoanStatusAPIView(mixins.RetrieveModelMixin, MFAPIView):
    lookup_url_kwarg = 'loanId'
    queryset = LoanApplication.objects
    serializer_class = LoanApplicationStatusSerializer

    def get(self, request, *args, **kwargs):
        """Loan Application Status API

        #TODO
        """

        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        instance = super().get_object()

        instance.lms_data = LoanApplicationData.objects.filter(app=instance
                                ).select_related('lms_api'
                                ).order_by('lms_api__priority', '-created')

        instance.lender_data = LoanData.objects.filter(app=instance
                                ).select_related('lender_api'
                                ).order_by('lender_api__priority', '-created')

        lms_api = LoanManagementSystemAPI.objects.filter(lms=instance.lms)
        lender_api = LenderSystemAPI.objects.filter(lender=instance.lender)

        lms_api_success = {}
        lms_api_failure = {}

        for each in lms_api:
            lms_api_success.update({each.pk: False})

        for each in instance.lms_data:
            if status.is_success(each.response_code):
                lms_api_success.update({each.lms_api.pk: True})
                lms_api_failure.pop(each.lms_api.pk, None)

            elif not lms_api_success.get(each.lms_api.pk):
                lms_api_failure.update({each.lms_api.pk: True})

        lender_api_success = {}
        lender_api_failure = {}

        for each in lender_api:
            lender_api_success.update({each.pk: False})

        for each in instance.lender_data:
            if status.is_success(each.response_code):
                lender_api_success.update({each.lender_api.pk: True})
                lender_api_failure.pop(each.lender_api.pk, None)

            elif not lender_api_success.get(each.lender_api.pk):
                lender_api_failure.update({each.lender_api.pk: True})

        if all(lms_api_success.values()) and all(lender_api_success.values()):
            instance.status = 'SUBMITTED'

        elif all(lms_api_success.values()) and not len(instance.lender_data):
            instance.status = 'FETCHED'

        elif len(lms_api_failure) or len(lender_api_failure):
            instance.status = 'FAILED'
        else:
            instance.status = 'PENDING'

        return instance
