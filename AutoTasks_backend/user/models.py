from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, discord_user_id, **extra_fields):
        if not discord_user_id:
            raise ValueError(_('The discord user id number must be set'))

        user = self.model(discord_user_id=discord_user_id, **extra_fields)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    discord_user_id = models.CharField(_('discord user id'), unique=True, max_length=30)

    USERNAME_FIELD = 'discord_user_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.discord_user_id

    # Override password methods because there is no password
    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        return True
