from rest_framework.response import Response


def response_200(data):
    return Response({
        "error": False,
        "errorMsg": "Success",
        "data": data
    }, status=200)


def response_400(error_msg):
    return Response({
        "error": True,
        "errorMsg": error_msg,
        "data": None
    }, status=400)


def response_500(error_msg):
    return Response({
        "error": True,
        "errorMsg": error_msg,
        "data": None
    }, status=500)