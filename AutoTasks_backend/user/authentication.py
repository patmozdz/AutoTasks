from django.contrib.auth.backends import BaseBackend
from .models import User


class PhoneAuthenticationBackend(BaseBackend):
    def authenticate(self, request, phone=None):
        try:
            user = User.objects.get(phone=phone)

            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
