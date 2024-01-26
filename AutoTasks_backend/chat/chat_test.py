import os
import django
import sys

# Windows setup below
# sys.path.append("C:/Users/Papis/Documents/~GitHub Projects/AutoTasks/AutoTasks_backend")
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutoTasks_backend.settings')
# django.setup()

# Linux setup below
sys.path.append("/mnt/c/Users/Papis/Documents/~GitHub Projects/AutoTasks/AutoTasks_backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutoTasks_backend.settings')
django.setup()

from rest_framework import status
from django.contrib.auth import authenticate
from twilio.twiml.messaging_response import MessagingResponse
from chat.models import Chat
from django.contrib.auth import get_user_model
User = get_user_model()


def pretend_receive_sms_from_twilio(request):
    body = request.get('Body', None)
    phone = request.get('From', None)

    if not body or not phone:
        return {"error": "Invalid data."}, status.HTTP_400_BAD_REQUEST

    user = authenticate(phone=phone)  # Modified to use username=phone
    if user:
        end_choices = ['END', 'STOP', 'QUIT', 'EXIT', 'UNSUBSCRIBE', 'CANCEL']
        if body in end_choices:
            # TODO: Handle user unsubscribing, maybe delete account?
            resp = MessagingResponse()
            resp.message("You have been unsubscribed.")
        else:
            # Handle user sending a message
            resp = MessagingResponse()
            chat_response = Chat.chat_completion_from_sms_body(user, body)
            resp.message = chat_response.choices[0].message.content
    else:
        # Handle unauthenticated user
        new_user = User.objects.create_user(phone=phone)  # Modified to use username=phone
        new_user.save()
        resp = MessagingResponse()
        resp.message = "Thank you for registering! Please type to engage with the autotasker."

    return resp.message, status.HTTP_200_OK


import warnings  # Temporarily ignore the timezone warning

# Filter out the specific RuntimeWarning
warnings.filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning
)


if __name__ == '__main__':
    # This is a simulation
    phone_number = input("Phone number: ")
    while True:
        simulated_text_message = input("Send sms: ")
        pretend_request = {'Body': simulated_text_message, 'From': phone_number}

        if simulated_text_message == "quit":
            break

        response, status_code = pretend_receive_sms_from_twilio(pretend_request)
        print(response)

# Features of most recent simulation:
# ChatGPT can now remind you when reminders trigger and reschedule them/continuously remind you if you don't reply
