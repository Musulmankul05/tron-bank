from django.db import models
from django.contrib.auth.models import AbstractUser

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
    date_birth = models.DateField(blank=True, null=True)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(null=True, blank=True)

class BackupCodesModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='backups')
    code = models.CharField(max_length=128, blank=True, null=True)

class KYCModel(models.Model):
    ACCOUNT_TYPE = (
        ('STANDART', 'Private node'),
        ('BUSINESS', 'Corporate node')
    )
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='kyc')
    inn = models.BigIntegerField(null=True, blank=True)
    account_type = models.CharField(choices=ACCOUNT_TYPE, default='STANDART')
    signature_svg = models.TextField(blank=True, null=True)