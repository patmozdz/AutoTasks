import redis
import json
from celery import shared_task
from datetime import datetime
from django.db import transaction
from .models import Reminder
from chat.models import Chat
from AutoTasks_backend import secrets_manager
from zoneinfo import ZoneInfo

# Set up Redis client using an environment variable (redis is used to communicate with the Discord bot)
redis_url = secrets_manager.DISCORD_BOT_BROKER_URL
redis_client = redis.Redis.from_url(redis_url)


# This task is run in 'AutoTasks_backend/celery.py' every minute
@shared_task
def watch_for_reminder_time():
    timezone = ZoneInfo('America/Chicago')  # TODO: Maybe use the user's timezone instead of hardcoding it to Chicago
    current_time = datetime.now(timezone)

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
                print(response_message)  # For testing, prints to Celery worker's console

                # Enqueue the message into Redis for the Discord bot to process
                message_data = {
                    'discord_user_id': user.discord_user_id,
                    'body': response_message
                }
                redis_client.lpush('discord_queue', json.dumps(message_data))  # Use json.dumps to serialize the message data to a JSON string before storing in Redis

            except Exception as e:
                print(e)
