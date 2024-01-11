import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutoTasks_backend.settings')

app = Celery('AutoTasks_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'watch-for-reminder-time-every-minute': {
        'task': 'reminders.tasks.watch_for_reminder_time',
        'schedule': crontab(minute='*'),
    },
}
