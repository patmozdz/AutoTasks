from celery import shared_task
from datetime import datetime
from django.db import transaction
from .models import Reminder
from chat.models import Chat
from AutoTasks_backend import secrets_manager
from twilio.rest import Client


# Set up Twilio client
client = Client(secrets_manager.TWILIO_ACCOUNT_SID, secrets_manager.TWILIO_AUTH_TOKEN)


# This task is run in 'AutoTasks_backend/celery.py' every minute
@shared_task
def watch_for_reminder_time():
    current_time = datetime.now()

    with transaction.atomic():  # Used to treat transaction as a single unit of work, so if one operation fails then all are rolled back. select_for_update() is used to lock the row until the end of the transaction to prevent race conditions between delete_reminder() and watch_for_reminder_time()
        reminders = Reminder.objects.filter(reminder_time__lte=current_time).select_for_update()
        for reminder in reminders:
            try:
                user = reminder.user
                response = Chat.chat_completion_from_reminder(user, reminder)

                # Moved setting reminder.notified to True to chat_completion_from_reminder() in chat/models.py because the chat completion can delete or edit the reminder, and so if we do it here
                # then we can potentially be working on a reminder object that no longer exists in the database, and therefore be overwriting any adjustments or deletions.
                # Plus, it's more logical to change reminder.notified to True right after adding the notification message.

                # Below is for testing purposes, below should print to Celery worker's console. In production this should relay the message to the user's phone number by calling Twilio API.
                response_message = response.choices[0].message.content
                print(response_message)

            except Exception as e:
                print(e)
