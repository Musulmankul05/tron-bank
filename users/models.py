from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField

class UserModel(AbstractUser):
    STATUS = (
        ("PEN", "Pending"),
        ("UNV", "Unverified"),
        ("VER", "Verified"),
        ("REJ", "Rejected")
    )
    kyc_status = models.CharField(max_length = 3, choices = STATUS, default="UNV")
    phone = models.CharField(max_length=32, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    date_birth = models.DateField()
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    country = CountryField()

class KYCModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='user')
    