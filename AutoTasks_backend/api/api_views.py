from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from chat.models import Chat
from django.contrib.auth import get_user_model
from AutoTasks_backend import secrets_manager
from api.utils import validate_internal


User = get_user_model()


@api_view(['POST'])
@validate_internal  # Decorator to validate the request is made from an internal script
def discord_webhook(request):
    data = request.data  # This is used because the request should contain JSON data
    body = data.get('content', None)
    discord_user_id = data.get('user_id', None)

    if not body or not discord_user_id:
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(discord_user_id=discord_user_id)
    resp_body = ""

    if user:
        end_choices = ['END', 'STOP', 'QUIT', 'EXIT', 'UNSUBSCRIBE', 'CANCEL']
        delete_choices = ['DELETE', 'REMOVE', 'UNSUBSCRIBE', 'CANCEL', 'DELETE ACCOUNT', 'REMOVE ACCOUNT']

        if body.lower() == 'help':
            resp_body = "Reply with END to unsubscribe. Reply with DELETE to delete your account."
        elif body in end_choices:
            # TODO: Add a confirmation step, like "Are you sure you want to unsubscribe? Reply with UNSUBSCRIBE to confirm."
            # TODO: Handle soft deleting the user
            resp_body = "You have been unsubscribed from the AutoTasker. To resubscribe, reply with the registration code."
        elif body.lower() in delete_choices:
            # Hard delete the user
            # TODO: Add a confirmation step, like "Are you sure you want to delete your account? Reply with DELETE MY ACCOUNT to confirm."
            User.objects.delete_user(user, soft_delete=False)
            resp_body = "Your account has been deleted."
        else:
            # Send the message to ChatGPT
            chat_response = Chat.chat_completion_from_sms_body(user, body)
            resp_body = chat_response.choices[0].message.content
    else:
        # Handle unauthenticated user
        if body == "REGISTER":
            # New user welcome message
            resp_body = "Thank you for messaging! Please reply with the registration code to engage with the AutoTasker."

        elif body == secrets_manager.REGISTRATION_CODE:
            new_user = User.objects.create_user(discord_user_id=discord_user_id)
            new_user.save()
            resp_body = "Thank you! You have been registered. Type anything to engage with the AutoTasker. Note: Responses are currently limited to a certain amount of tokens to avoid overcharging, so they may get abruptly cut off."

        else:
            # Unauthenticated user sends a random message, respond with nothing
            resp_body = ""  # Right now generates an error (400 Bad Request (error code: 50006): Cannot send an empty message), TODO: fix this

    return Response({"body": resp_body}, status=status.HTTP_200_OK)  # content_type='application/json' by default when using dictionaries in DRF
