from rest_framework import serializers

from borrowers.models import LoanApplication, LoanApplicationData
from lenders.models import LoanData



class LoanApplicationRequestSerializer(serializers.ModelSerializer):

    lmsid = serializers.CharField(max_length=255)
    lms_code = serializers.CharField(max_length=10)
    lender_code = serializers.CharField(max_length=10)
    partner_code = serializers.CharField(max_length=10, allow_blank=True,
                        required=False, help_text='Channel Partner Code')

    class Meta:
        model = LoanApplication
        fields = ('lmsid', 'lms_code', 'lender_code', 'partner_code')



class LoanApplicationResponseSerializer(serializers.ModelSerializer):

    application_id = serializers.CharField(source='pk')

    class Meta:
        model = LoanApplication
        fields = ('application_id',)



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

    task_name = serializers.CharField()
    task_status = serializers.CharField()
