from base.filters import BaseAutocompleteFilter
from .models import LoanApplication



class LMSNestedFilter(BaseAutocompleteFilter):
    title = 'LMS'
    field_name = 'lms'
    parameter_name = 'app__lms'
    nested_model = LoanApplication



class AppFilter(BaseAutocompleteFilter):
    title = 'Application'
    field_name = 'app'
