from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .validators import phonenumber_validator
from django.utils import timezone
from datetime import timedelta
from django.utils.crypto import get_random_string


class User(AbstractUser) :

    username = models.CharField(
        _('phone number'),
        max_length=13,
        unique=True,
        help_text=_('Required. 13 or 11 digits .'),
        validators=[phonenumber_validator,],
        error_messages={
            'unique': _("A user with that phone number already exists."),
        },
    )

    city = models.CharField("city" , max_length=64 , default="" , blank=True)
    introduction_method = models.CharField("introduction method" , max_length=128 , default="")


class SmsVerificationCode (models.Model) :
    phone_number = models.CharField(_("phone number"),max_length=13)
    code = models.CharField(_("code") , max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) :

        time_difference = timezone.now() - self.created_at
        if time_difference < timedelta(seconds=60):
            return False
        return True

    def timeout_time(self) :

        time_difference = timezone.now() - self.created_at
        if (60 - time_difference.seconds) < 0:
            return 0
        return (60 - time_difference.seconds)

    def __str__(self) :
        return self.phone_number


class UserRegistrationIdentity (models.Model):
    identity = models.CharField(verbose_name="کد شناسایی" , max_length=32)
    phone_number = models.CharField(verbose_name="شماره تلفن" , max_length=14)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.identity:
            self.identity = get_random_string(length=32)
        super(UserRegistrationIdentity, self).save(*args, **kwargs)


    def is_valid(self) :
        time_difference = timezone.now() - self.created_at
        if time_difference > timedelta(minutes=15):
            return False
        return True