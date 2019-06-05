from rest_framework.response import Response
from rest_framework import status


def class_view_authorize(method):
    def wrap(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return method(self, request, *args, **kwargs)
        else:
            def unauthorize_handle(self, request, *args, **kwargs):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return unauthorize_handle(self, request, *args, **kwargs)
    return wrap
