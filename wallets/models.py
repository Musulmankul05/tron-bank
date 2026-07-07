from django.db import models

from users.models import UserModel

# Create your models here.
class WalletModel(models.Model):
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="wallets")
    currency = models.CharField()