from celery import shared_task
from django.utils import timezone
from .models import Reminder
from chat.models import Chat


# Periodic task setup can be found in .management/commands/setup_periodic_tasks.py. This is because the setup needs to only happen once after deployment,
# which will be handled by Docker
@shared_task
def watch_for_reminder_time():
    current_time = timezone.now()
    reminders = Reminder.objects.filter(reminder_time__lte=current_time, notified=False)  # TODO: Add flag to database 'notified'
    for reminder in reminders:
        user = reminder.user
        Chat.chat_completion_from_reminder(user, reminder)
        reminder.notified = True  # Flag to indicate notification was sent
        reminder.save()
