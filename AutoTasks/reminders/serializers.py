from rest_framework import serializers
from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['user_id', 'title', 'description', 'reminder_time', 'recurring_interval', 'urgency']
