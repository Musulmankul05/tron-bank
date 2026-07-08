from django.db import models

from users.models import UserModel

# Create your models here.
class CardModel(models.Model):
    CURRENCIES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('KGS', 'Som'),
    ]
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="cards")
    name = models.CharField(max_length=64, default='My Card')
    currency = models.CharField(choices=CURRENCIES, max_length=3, default='KGS', editable=False)
    balance = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    favorite = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.favorite:
            CardModel.objects.filter(owner=self.owner, favorite=True).exclude(pk=self.pk).update(favorite=False)
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner'], condition=models.Q(favorite=True), name='unique_user_wallet_favorite'),
            models.UniqueConstraint(fields=['owner', 'currency'], name='unique_user_wallet_currency')
        ]