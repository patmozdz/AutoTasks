from .models import edit_reminder


def send_notification(user_id, reminder_id):
    """
    Sends a notification for a reminder.
    """
    reminder = Reminder.objects.get(id=reminder_id, user_id=user_id)
    # Here you can implement the logic to send a notification
    # For example, you can send an email or a push notification
