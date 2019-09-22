from rest_framework.response import Response

class ApiResponse(Response):
    def __init__(self, data, message="", *args, **kwargs):
        payload = { 
            "payload": data,
            "message": message
        }
        super().__init__(payload, *args, **kwargs)
        self['API_VERSION'] = 1.0