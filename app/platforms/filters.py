from base.filters import BaseAutocompleteFilter
from .models import *



class LMSAPIFilter(BaseAutocompleteFilter):
    title = 'LMS API'
    field_name = 'lms_api'



class LMSFilter(BaseAutocompleteFilter):
    title = 'LMS'
    field_name = 'lms'



class LMSNestedFilter(BaseAutocompleteFilter):
    title = 'LMS'
    field_name = 'lms'
    parameter_name = 'lms_api__lms'
    nested_model = LoanManagementSystemAPI



class SVCAPIFilter(BaseAutocompleteFilter):
    title = 'SVC API'
    field_name = 'svc_api'



class SVCFilter(BaseAutocompleteFilter):
    title = 'SVC'
    field_name = 'svc'



class SVCNestedFilter(BaseAutocompleteFilter):
    title = 'SVC'
    field_name = 'svc'
    parameter_name = 'svc_api__svc'
    nested_model = PlatformServiceAPI



