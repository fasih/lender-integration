from rest_framework.exceptions import APIException


class MFAPIException(APIException):

    def __init__(self, detail=None, code=None, **kwargs):
        super().__init__(detail, code)
        self.kwargs = kwargs

    def get_full_details(self):
        data = super().get_full_details()
        data.update(self.kwargs)
        return data
