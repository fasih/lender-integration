from rest_framework import status
from API.exceptions import MFAPIException



class LoanApplicationAlreadyExist(MFAPIException):
    default_code = 'LAAE'
    default_detail = 'Loan Application Already Exist'
    status_code = status.HTTP_400_BAD_REQUEST



class LoanApplicationServerError(MFAPIException):
    default_code = 'LASE'
    default_detail = 'Loan Application Server Error'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
