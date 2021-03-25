import structlog as logging

from django.db.utils import IntegrityError

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from drf_yasg2.utils import swagger_auto_schema

from .serializers import *
from .execptions import *

from API.views import MFAPIView
from base.utils import apply_task
from lenders.models import *
from platforms.models import *

logger = logging.getLogger(__name__)

SYNC = False



class LoanApplicationCreateAPIView(MFAPIView):
    serializer_class = LoanApplicationCreateSerializer

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: 
        LoanApplicationTaskSerializer()})
    def post(self, request, *args, **kwargs):
        """Loan Application Create API

        API fetches borrower loan application from LMS and other services then
        create lender loan application.
        """        

        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        from .tasks import loans_post
        apply_task(loans_post.s(instance.pk), SYNC)
        instance.task_name = loans_post.name
        instance.task_status = "Submitted"
        app = LoanApplicationTaskSerializer(instance)

        return Response(app.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        lms = generics.get_object_or_404(LoanManagementSystem.objects,
                    code=serializer.data['lms_code'])

        lender = generics.get_object_or_404(LenderSystem.objects,
                    code=serializer.data['lender_code'])

        if serializer.data.get('cp_code'):
            cp = generics.get_object_or_404(ChannelPartners.objects,
                        code=serializer.data['cp_code'])
        else:
            cp = None

        if serializer.data.get('svc_code'):
            svc = PlatformService.objects.filter(
                        code__in=serializer.data['svc_code'])
        else:
            svc = []

        instance = LoanApplication(lmsid=serializer.data['loan_id'], lms=lms,
                                    lender=lender, cp=cp)
        try:
            instance.save()
            [instance.svc.add(i) for i in svc]
        except IntegrityError:
            raise LoanApplicationAlreadyExist()

        return instance



class LoanApplicationAPIView(MFAPIView):
    lookup_url_kwarg = 'application_id'
    queryset = LoanApplication.objects
    serializer_class = LoanApplicationStatusSerializer

    def get(self, request, *args, **kwargs):
        """Loan Application Status API

        API fetches status of all APIs related to the loan application
        """

        instance = self.get_object()
        instance = self.get_status(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=serializers.Serializer,
        responses={status.HTTP_200_OK: LoanApplicationTaskSerializer()})
    def patch(self, request, *args, **kwargs):
        """Loan Application LMS API

        API submits a task to fetch loan application from the LMS
        by calling LMS APIs in the background.
        """        
        instance = self.get_object()
        from .tasks import loans_patch
        apply_task(loans_patch.s(instance.pk), SYNC)
        instance.task_name = loans_patch.name
        instance.task_status = "Submitted"
        app = LoanApplicationTaskSerializer(instance)

        return Response(app.data)

    @swagger_auto_schema(request_body=serializers.Serializer,
        responses={status.HTTP_200_OK: LoanApplicationTaskSerializer()})
    def put(self, request, *args, **kwargs):
        """Loan Application Lender API

        API submits a task to create loan application at the Lender
        by calling Lender APIs in the background.
        """        

        instance = self.get_object()
        from .tasks import loans_put
        apply_task(loans_put.s(instance.pk), SYNC)
        instance.task_name = loans_put.name
        instance.task_status = "Submitted"
        app = LoanApplicationTaskSerializer(instance)

        return Response(app.data)

    def get_status(self, instance):
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
