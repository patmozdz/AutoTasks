from rest_framework import viewsets
from rest_framework.response import Response
from .models import Reminder, create_reminder, edit_reminder, delete_reminder
from .serializers import ReminderSerializer


class ReminderViewSet(viewsets.ViewSet):
    def create(self, request):
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        description = request.data.get('description')
        reminder_time = request.data.get('reminder_time')
        recurring_interval = request.data.get('recurring_interval')
        urgency = request.data.get('urgency')

        reminder = create_reminder(user_id, title, description, reminder_time, recurring_interval, urgency)
        serializer = ReminderSerializer(reminder)

        return Response(serializer.data)

    def update(self, request, pk=None):
        reminder_id = pk
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        description = request.data.get('description')
        reminder_time = request.data.get('reminder_time')
        recurring_interval = request.data.get('recurring_interval')
        urgency = request.data.get('urgency')

        reminder = edit_reminder(reminder_id, user_id, title, description, reminder_time, recurring_interval, urgency)
        serializer = ReminderSerializer(reminder)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user_id = request.data.get('user_id')
        reminder_id = pk

        delete_reminder(user_id, reminder_id)

        return Response({'status': 'Reminder deleted'})
