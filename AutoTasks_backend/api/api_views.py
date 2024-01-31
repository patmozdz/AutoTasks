from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from twilio.twiml.messaging_response import MessagingResponse
from chat.models import Chat
from django.contrib.auth import get_user_model
from AutoTasks_backend import secrets_manager
from api.utils import validate_request_from_twilio
from django.http import HttpResponse


User = get_user_model()


@api_view(['POST'])
@validate_request_from_twilio  # Decorator to validate the request is from Twilio
def receive_sms_from_twilio(request):
    body = request.POST.get('Body', None)
    phone = request.POST.get('From', None)

    if not body or not phone:
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(phone=phone)
    resp = MessagingResponse()

    if user:
        end_choices = ['END', 'STOP', 'QUIT', 'EXIT', 'UNSUBSCRIBE', 'CANCEL']
        if body in end_choices:
            # TODO: Handle user unsubscribing, maybe delete account?
            resp.message("You have been unsubscribed.")
        else:
            # Handle user sending a message
            chat_response = Chat.chat_completion_from_sms_body(user, body)
            resp.message(chat_response.choices[0].message.content)
    else:
        # Handle unauthenticated user
        if body == "REGISTER":
            resp.message("Thank you for messaging! Please reply with the registration code to engage with the AutoTasker.")

        elif body == secrets_manager.REGISTRATION_CODE:
            new_user = User.objects.create_user(phone=phone)  # Assuming username=phone
            new_user.save()
            resp.message("Thank you! You have been registered. Type anything to engage with the AutoTasker. Note: Responses are currently limited to a certain amount of tokens to avoid overcharging, so they may get abruptly cut off. Currently using Twilio trial account, so ignore the 'Sent from your Twilio trial account' message.")

        else:
            # Unauthenticated user sends a random message, respond with nothing
            resp.message("")  # Just pass here, the empty response will be handled below

    # When using Response, the xml gets incorrectly surrounded by quotes
    # return Response(resp.to_xml(), content_type='application/xml')

    # Use HttpResponse for now, find better solution
    return HttpResponse(str(resp), content_type='application/xml')
