from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {"success": False, "message": "server_error"},
            status=500
        )

    data = response.data

    message = "invalid"


    if isinstance(data, dict) and "detail" in data:
        message = data["detail"]

   
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and value:
                message = value[0]
                break


    elif isinstance(data, list) and data:
        message = data[0]

    response.data = {
        "success": False,
        "message": message
    }

    return response
