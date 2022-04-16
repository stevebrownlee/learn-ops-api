from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

def is_instructor():
    def decorator(func):
        def __wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name='Instructors').exists():
                return func(request, *args, **kwargs)
            else:
                return Response(
                    {'message': 'You must be an instructor'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return __wrapper
    return decorator

def is_staff():
    def decorator(func):
        def __wrapper(request, *args, **kwargs):
            if request.user.groups.filter(Q(name='Staff') | Q(name='Instructors')).exists():
                return func(request, *args, **kwargs)
            else:
                return Response(
                    {'message': 'You must be NSS staff'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return __wrapper
    return decorator
