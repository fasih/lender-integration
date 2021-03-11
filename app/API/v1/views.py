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
from lenders.models import LenderSystem
from platforms.models import ChannelPartners, LoanManagementSystem



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
    lookup_url_kwarg = 'application_id'
    serializer_class = LoanApplicationStatusSerializer
    queryset = LoanApplicationStatusSerializer.Meta.model.objects

    def get(self, request, *args, **kwargs):
        """Loan Application Status API

        #TODO
        """

        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        instance = super().get_object()

        instance.lms_status = LoanApplicationData.objects.filter(app=instance
                                ).order_by('lms_api__priority')

        instance.lender_status = LoanData.objects.filter(app=instance
                                ).order_by('lender_api__priority')
        return instance
