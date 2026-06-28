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
    kyc_status = models.CharField(max_length = 3, choices = STATUS, default="UNV", null=False)
    phone = models.CharField(max_length=32, null=False, blank=False, unique=True)
    date_birth = models.DateField(blank=False, null=False)
    country = CountryField(null=False, blank=False)