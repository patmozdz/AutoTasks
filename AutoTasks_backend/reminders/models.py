from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction
User = get_user_model()


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
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder({self.id}, '{self.title}', '{self.description}', '{self.reminder_time}', '{self.recurring_interval}', '{self.urgency}')"

    ###
    # These functions (below) cannot be an API because ChatGPT needs to be able to call them
    ###
    @classmethod
    def create_reminder(cls, user, title, description, reminder_time, recurring_interval=None, urgency=None):
        """
        Creates a new reminder.
        """
        reminder = cls(user=user, title=title, description=description, reminder_time=reminder_time, recurring_interval=recurring_interval, urgency=urgency)

        reminder.save()

        return f'Created reminder: {reminder}'

    @classmethod
    def edit_reminder(cls, user, reminder_id, title=None, description=None, reminder_time=None, recurring_interval=None, urgency=None):
        """
        Edits an existing reminder.
        """
        reminder = cls.objects.get(user=user, id=reminder_id)
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
        return f'Edited reminder. New values: {reminder}'

    @classmethod
    def delete_reminder(cls, user, reminder_id):
        """
        Deletes an existing reminder.
        """

        with transaction.atomic():  # Used to treat transaction as a single unit of work, so if one operation fails then all are rolled back. select_for_update() is used to lock the row until the end of the transaction to prevent race conditions between delete_reminder() and watch_for_reminder_time()
            reminder = cls.objects.filter(user=user, id=reminder_id).select_for_update().first()
            if reminder:
                reminder.delete()
                return f'Deleted reminder with id {reminder_id}'
            else:
                return f'Reminder with id {reminder_id} not found or already processed.'
