from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, **extra_fields):
        if not phone:
            raise ValueError(_('The Phone number must be set'))

        user = self.model(phone=phone, **extra_fields)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(_('phone number'), unique=True, max_length=15)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    # Override password methods because there is no password
    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        return True
