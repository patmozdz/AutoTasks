from django.conf import settings
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from functools import wraps
from rest_framework import status
from rest_framework.response import Response
from AutoTasks_backend import secrets_manager


def validate_internal(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header != f'Token {secrets_manager.INTERNAL_TOKEN}':
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        return view_func(request, *args, **kwargs)
    return _wrapped_view
