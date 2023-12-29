from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = 'Sets up the periodic task for watching reminders'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        task_name = 'Watch for Reminder Time Every Minute'
        if not PeriodicTask.objects.filter(name=task_name).exists():
            PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task='reminders.tasks.watch_for_reminder_time',
            )
            self.stdout.write(self.style.SUCCESS('Successfully set up periodic task'))
        else:
            self.stdout.write(self.style.WARNING('Periodic task already exists'))
