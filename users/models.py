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
    phone = models.CharField(max_length=32)
    date_birth = models.DateField()
    country = CountryField()