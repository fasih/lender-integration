from rest_framework import status
from API.exceptions import MFAPIException



class LoanApplicationAlreadyExist(MFAPIException):
    default_code = 'LAAE'
    default_detail = 'Loan Application Already Exist with Given LMS'
    status_code = status.HTTP_400_BAD_REQUEST
