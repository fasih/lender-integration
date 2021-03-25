from rest_framework import serializers

from borrowers.models import LoanApplication, LoanApplicationData
from lenders.models import LoanData
from .choices import *



class LoanApplicationCreateSerializer(serializers.ModelSerializer):

    loan_id = serializers.CharField(max_length=255, label='Loan ID',
                        help_text='Loan Application Reference No. at LMS')

    lms_code = serializers.ChoiceField(choices=LMS_CHOICES, label='LMS Code',
                        help_text='Loan Management System Code')

    lender_code = serializers.ChoiceField(choices=LENDER_CHOICES,
                        label='Lender Code', help_text='Lender System Code')

    svc_code = serializers.MultipleChoiceField(choices=SVC_CHOICES,
                        allow_blank=True, required=False, label='SVC Code',
                        help_text='List of Services Code')

    cp_code = serializers.ChoiceField(choices=CP_CHOICES, allow_blank=True,
                        required=False, label='CP Code',
                        help_text='Channel Partner Code')


    class Meta:
        model = LoanApplication
        fields = ('loan_id', 'lms_code', 'lender_code', 'svc_code', 'cp_code')



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

    status = serializers.CharField()
    lms_status = LoanApplicationDataSerializer(source='lms_data', many=True)
    lender_status = LoanDataSerializer(source='lender_data', many=True)

    class Meta:
        model = LoanApplication
        fields = ('status', 'lms_status', 'lender_status')



class LoanApplicationTaskSerializer(serializers.Serializer):

    application_id = serializers.CharField(source='pk')
    task_name = serializers.CharField()
    task_status = serializers.CharField()
