from rest_framework import status
from API.exceptions import MFAPIException



class LoanApplicationAlreadyExist(MFAPIException):
    default_code = 'LAAE'
    default_detail = 'Loan Application Already Exist'
    status_code = status.HTTP_400_BAD_REQUEST
