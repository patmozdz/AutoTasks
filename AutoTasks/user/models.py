from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(_('phone number'), unique=True, max_length=15)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = BaseUserManager()

    def __str__(self):
        return self.phone

    # Override password methods because there is no password
    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        return True
