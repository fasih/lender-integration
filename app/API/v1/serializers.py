from rest_framework import serializers

from borrowers.models import LoanApplication, LoanApplicationData
from lenders.models import LoanData
from .choices import *



class LoanApplicationCreateSerializer(serializers.ModelSerializer):

    loan_id = serializers.CharField(max_length=255, label='Loan ID',
                        help_text='Loan Application ID at LMS')

    lms_code = serializers.ChoiceField(choices=LMS_CHOICES, label='LMS Code',
                        help_text='Loan Management System Code')

    lender_code = serializers.ChoiceField(choices=LENDER_CHOICES,
                        label='Lender Code', help_text='Lender System Code')

    '''
    cp_code = serializers.ChoiceField(choices=CP_CHOICES, allow_blank=True,
                        required=False, label='CP Code',
                        help_text='Channel Partner Code')

    svc_code = serializers.MultipleChoiceField(choices=SVC_CHOICES,
                        allow_blank=True, required=False, label='SVC Code',
                        help_text='List of Services Code')

    lms_actions = serializers.ListField(child=serializers.CharField(
                        label='LMS Action Code'),
                        allow_empty=True, required=False,
                        help_text='List of actions performed at LMS')
    '''


    class Meta:
        model = LoanApplication
        fields = ('loan_id', 'lms_code', 'lender_code')



class LoanDataSerializer(serializers.ModelSerializer):

    api_name = serializers.CharField(source='lender_api.name')

    class Meta:
        model = LoanData
        fields = ('api_name', 'response_code')



class LoanApplicationDataSerializer(serializers.ModelSerializer):

    api_name = serializers.CharField(source='lms_api.name')

    class Meta:
        model = LoanApplicationData
        fields = ('api_name', 'response_code')



class LoanApplicationStatusSerializer(serializers.ModelSerializer):

    task_name = serializers.CharField(required=False)
    task_status = serializers.ChoiceField(required=False, choices=TASK_STATUS.choices)
    workflow_status = serializers.ChoiceField(choices=WORKFLOW_STATUS.choices)
    lms_api_status = LoanApplicationDataSerializer(source='lms_data', many=True)
    lender_api_status = LoanDataSerializer(source='lender_data', many=True)

    class Meta:
        model = LoanApplication
        fields = ('task_name', 'task_status', 'workflow_status',
                    'lms_api_status', 'lender_api_status')



class LoanApplicationTaskSerializer(serializers.Serializer):

    application_id = serializers.CharField(source='pk')
    task_name = serializers.CharField()
    task_status = serializers.ChoiceField(choices=TASK_STATUS.choices)
