from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from twilio.twiml.messaging_response import MessagingResponse
from chat.models import Chat


@api_view(['POST'])
def receive_sms_from_twilio(request):
    body = request.POST.get('Body', None)
    phone = request.POST.get('From', None)

    if not body or not phone:
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, phone=phone)
    if user is not None:
        end_choices = ['END', 'STOP', 'QUIT', 'EXIT', 'UNSUBSCRIBE', 'CANCEL']
        if body in end_choices:
            # TODO: Handle user unsubscribing, maybe delete account?
            resp = MessagingResponse()
            resp.message("You have been unsubscribed.")
        else:
            # Handle user sending a message
            resp = MessagingResponse()
            chat_response = Chat.chat_completion_from_sms(user, body)
            resp.message = chat_response.choices[0].message.content
    else:
        # Handle unauthenticated user
        resp = MessagingResponse()
        resp.message("You are not registered.")

    # Do you need to send a message to the user or is sending the response enough?
    return Response(str(resp), status=status.HTTP_200_OK, content_type='text/xml')
