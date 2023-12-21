from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class Chat(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat'
    )
    chat_object = JSONField()

    def __str__(self):
        return f"Chat for {self.user.username}"
