from base.filters import BaseAutocompleteFilter
from .models import *



class LenderAPIFilter(BaseAutocompleteFilter):
    title = 'Lender API'
    field_name = 'lender_api'



class LenderFilter(BaseAutocompleteFilter):
    title = 'Lender'
    field_name = 'lender'



class LenderNestedFilter(BaseAutocompleteFilter):
    title = 'Lender'
    field_name = 'lender'
    parameter_name = 'lender_api__lender'
    nested_model = LenderSystemAPI



