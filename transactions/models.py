from django.db import models
import uuid
from wallets.models import WalletModel

class TransactionModel(models.Model):
    CHOICES = (
        ("PE", "Pending"),
        ("OK", "Completed"),
        ("NO", "Canceled"),
        ("ER", "Failed")
    )
    sender = models.ForeignKey(WalletModel, on_delete=models.CASCADE, related_name='sent')
    receiver = models.ForeignKey(WalletModel, on_delete=models.CASCADE, related_name='received')
    sent = models.DecimalField(decimal_places=4, max_digits=14)
    received = models.DecimalField(decimal_places=4, max_digits=14)
    exchange_rate = models.DecimalField(decimal_places=4, max_digits=14, null=True, blank=True)
    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    commission = models.DecimalField(decimal_places=4, max_digits=14, blank=True, null=True)
    encryption = models.BinaryField()
    status = models.CharField(choices=CHOICES, default="PE", max_length=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
