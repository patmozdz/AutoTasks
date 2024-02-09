from django.contrib.auth.backends import BaseBackend
from .models import User


class DiscordUserAuthenticationBackend(BaseBackend):
    def authenticate(self, request, discord_user_id=None):
        try:
            user = User.objects.get(discord_user_id=discord_user_id)

            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
