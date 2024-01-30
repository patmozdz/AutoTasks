from django.conf import settings
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from functools import wraps
from rest_framework import status
from rest_framework.response import Response
from AutoTasks_backend import secrets_manager


def validate_request_from_twilio(function):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(function)
    def decorated_function(request, *args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(secrets_manager.TWILIO_AUTH_TOKEN)

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.build_absolute_uri(),
            request.POST,
            request.META.get('HTTP_X_TWILIO_SIGNATURE', ''))

        # Continue processing the request if it's valid, return a 403 error if it's not
        if request_valid:
            return function(request, *args, **kwargs)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    return decorated_function


def send_sms_to_user(to, body):  # TODO: Implement or remove this
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to=to,
        from_=settings.TWILIO_PHONE_NUMBER,
        body=body,
    )
    return message.sid
