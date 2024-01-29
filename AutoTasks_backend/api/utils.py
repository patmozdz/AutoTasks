from django.conf import settings
from twilio.rest import Client


def send_sms_to_user(to, body):  # TODO: Implement or remove this
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to=to,
        from_=settings.TWILIO_PHONE_NUMBER,
        body=body,
    )
    return message.sid
