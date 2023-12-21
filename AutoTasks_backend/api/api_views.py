from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from twilio.twiml.messaging_response import MessagingResponse
from chat.utils import chat_completion_from_sms


@api_view(['POST'])
def receive_sms_from_twilio(request):
    body = request.POST.get('Body', None)
    phone = request.POST.get('From', None)

    if not body or not phone:
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, phone=phone)
    if user is not None:
        resp = MessagingResponse()
        chat_completion = chat_completion_from_sms(user, body)
        resp.message = chat_completion.choices[0].text
        # Proceed to do chatgpt stuff (remove you are already registered message)
    else:
        # Handle unauthenticated user
        resp = MessagingResponse()
        resp.message("You are not registered.")

    return Response(str(resp), status=status.HTTP_200_OK, content_type='text/xml')
