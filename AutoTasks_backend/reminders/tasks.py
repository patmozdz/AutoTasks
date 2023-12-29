from celery import shared_task
from django.utils import timezone
from .models import Reminder


# Periodic task setup can be found in .management/commands/setup_periodic_tasks.py. This is because the setup needs to only happen once after deployment,
# which will be handled by Docker
@shared_task
def watch_for_reminder_time():
    current_time = timezone.now()
    reminders = Reminder.objects.filter(reminder_time__lte=current_time, notified=False)  # TODO: Add flag to database 'notified'
    for reminder in reminders:
        initiate_chat(reminder)
        reminder.notified = True  # Flag to indicate notification was sent
        reminder.save()


def initiate_chat(reminder):
    # Logic to send email or notification
    pass
