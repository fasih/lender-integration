import structlog as logging

from django.core.cache import cache
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
from services.settings import TASK_SYNC


logger = logging.getLogger(__name__)



class LoanApplicationCreateAPIView(MFAPIView):
    serializer_class = LoanApplicationCreateSerializer

    @swagger_auto_schema(responses={
            status.HTTP_200_OK: LoanApplicationTaskSerializer,
            status.HTTP_201_CREATED: LoanApplicationTaskSerializer,
            status.HTTP_406_NOT_ACCEPTABLE: LoanApplicationTaskSerializer,
    })
    def post(self, request, *args, **kwargs):
        """Loan Application Create API

        API fetches borrower loan application from LMS and other services then
        create lender loan application.
        """        

        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance, created = self.perform_create(serializer)

        from .tasks import loans_post
        running_task = cache.get(instance.pk)

        if running_task:
            status_code = status.HTTP_406_NOT_ACCEPTABLE
            instance.task_name = running_task
            instance.task_status = "RUNNING"
        else:
            apply_task(loans_post.s(instance.pk), TASK_SYNC)
            status_code = created and status.HTTP_201_CREATED or status.HTTP_200_OK
            instance.task_name = loans_post.name
            instance.task_status = "SUBMITTED"

            cache.set(instance.pk, instance.task_name)

        app = LoanApplicationTaskSerializer(instance)

        return Response(app.data, status=status_code)

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
            svc = []
            for each in serializer.data['svc_code']:
                svc.append(generics.get_object_or_404(PlatformService.objects,
                            code=each))
        else:
            svc = []

        try:
            instance, created = LoanApplication.objects.get_or_create(
                                        lmsid=serializer.data['loan_id'],
                                        lms=lms, lender=lender, cp=cp)
            existing_svc = instance.svc.all()
            for each in svc:
                if each not in existing_svc:
                    instance.svc.add(each)
            logger.info('perform_create', view_name=self.get_view_name(), created=created)
        except Exception as e:
            logger.info('perform_create', view_name=self.get_view_name(), msg=str(e))
            raise LoanApplicationServerError()

        return instance, created



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
        responses={
            status.HTTP_200_OK: LoanApplicationTaskSerializer,
            status.HTTP_406_NOT_ACCEPTABLE: LoanApplicationTaskSerializer,
        },
    )
    def patch(self, request, *args, **kwargs):
        """Loan Application LMS API

        API submits a task to fetch loan application from the LMS
        by calling LMS APIs in the background.
        """        
        instance = self.get_object()

        from .tasks import loans_patch
        running_task = cache.get(instance.pk)

        if running_task:
            status_code = status.HTTP_406_NOT_ACCEPTABLE
            instance.task_name = running_task
            instance.task_status = "RUNNING"
        else:
            apply_task(loans_patch.s(instance.pk), TASK_SYNC)
            status_code = status.HTTP_200_OK
            instance.task_name = loans_patch.name
            instance.task_status = "SUBMITTED"

            cache.set(instance.pk, instance.task_name)

        app = LoanApplicationTaskSerializer(instance)

        return Response(app.data, status=status_code)

    @swagger_auto_schema(request_body=serializers.Serializer,
        responses={
            status.HTTP_200_OK: LoanApplicationTaskSerializer,
            status.HTTP_406_NOT_ACCEPTABLE: LoanApplicationTaskSerializer,
        },
    )
    def put(self, request, *args, **kwargs):
        """Loan Application Lender API

        API submits a task to create loan application at the Lender
        by calling Lender APIs in the background.
        """        
        instance = self.get_object()

        from .tasks import loans_put
        running_task = cache.get(instance.pk)

        if running_task:
            status_code = status.HTTP_406_NOT_ACCEPTABLE
            instance.task_name = running_task
            instance.task_status = "RUNNING"
        else:
            apply_task(loans_put.s(instance.pk), TASK_SYNC)
            status_code = status.HTTP_200_OK
            instance.task_name = loans_put.name
            instance.task_status = "SUBMITTED"

            cache.set(instance.pk, instance.task_name)

        app = LoanApplicationTaskSerializer(instance)

        return Response(app.data, status=status_code)

    def get_status(self, instance):
        instance.lms_data = []
        instance.lender_data = []

        lms_data = LoanApplicationData.objects.filter(app=instance
                                ).select_related('lms_api').active(
                                ).order_by('lms_api__priority', '-created')

        lender_data = LoanData.objects.filter(app=instance
                                ).select_related('lender_api').active(
                                ).order_by('lender_api__priority', '-created')

        lms_api = LoanManagementSystemAPI.objects.filter(lms=instance.lms).active()
        lender_api = LenderSystemAPI.objects.filter(lender=instance.lender).active()

        lms_api_list = []
        lms_api_success = {}
        lms_api_failure = {}

        for each in lms_api:
            lms_api_success.update({each.pk: False})
            lms_api_list.append(each)

        for each in lms_data:
            if each.lms_api not in lms_api_list:
                continue
            else:
                instance.lms_data.append(each)

            if status.is_success(each.response_code):
                lms_api_success.update({each.lms_api.pk: True})
                lms_api_failure.pop(each.lms_api.pk, None)

            elif not lms_api_success.get(each.lms_api.pk):
                lms_api_failure.update({each.lms_api.pk: True})

        lender_api_list = []
        lender_api_success = {}
        lender_api_failure = {}

        for each in lender_api:
            lender_api_success.update({each.pk: False})
            lender_api_list.append(each)

        for each in lender_data:
            if each.lender_api not in lender_api_list:
                continue
            else:
                instance.lender_data.append(each)

            if status.is_success(each.response_code):
                lender_api_success.update({each.lender_api.pk: True})
                lender_api_failure.pop(each.lender_api.pk, None)

            elif not lender_api_success.get(each.lender_api.pk):
                lender_api_failure.update({each.lender_api.pk: True})

        if all(lms_api_success.values()) and all(lender_api_success.values()):
            workflow_status = 'COMPLETED'

        elif all(lms_api_success.values()) and not len(instance.lender_data):
            workflow_status = 'LMS FETCHED'

        elif len(lms_api_failure) or len(lender_api_failure):
            workflow_status = 'FAILED'
        else:
            workflow_status = 'NOT COMPLETED'

        running_task = cache.get(instance.pk)
        if running_task:
            instance.task_name = running_task
            instance.task_status = "RUNNING"
        else:
            instance.workflow_status = workflow_status

        return instance
