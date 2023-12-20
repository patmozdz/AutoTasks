from django.db import models
from User import User


class Reminder(models.Model):
    URGENCY_CHOICES = [
        (1, '1 - Lowest'),
        (2, '2'),
        (3, '3 - Medium'),
        (4, '4'),
        (5, '5 - Highest'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reminder_time = models.DateTimeField()
    recurring_interval = models.IntegerField(null=True, blank=True)  # Assuming interval in minutes
    urgency = models.IntegerField(choices=URGENCY_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.title


def create_reminder(user_id, title, description, reminder_time, recurring_interval=None, urgency=None):
    """
    Creates a new reminder.
    """
    reminder = Reminder(user_id=user_id, title=title, description=description, reminder_time=reminder_time, recurring_interval=recurring_interval, urgency=urgency)
    reminder.save()


def edit_reminder(user_id, reminder_id, title=None, description=None, reminder_time=None, recurring_interval=None, urgency=None):
    """
    Edits an existing reminder.
    """
    reminder = Reminder.objects.get(id=reminder_id, user_id=user_id)
    if title is not None:
        reminder.title = title
    if description is not None:
        reminder.description = description
    if reminder_time is not None:
        reminder.reminder_time = reminder_time
    if recurring_interval is not None:
        reminder.recurring_interval = recurring_interval
    if urgency is not None:
        reminder.urgency = urgency
    reminder.save()


def delete_reminder(user_id, reminder_id):
    """
    Deletes an existing reminder.
    """
    Reminder.objects.filter(id=reminder_id, user_id=user_id).delete()
