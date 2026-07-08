from django.db import transaction
from transactions.models import TransactionModel
from decimal import Decimal

def execute_transfer(sender_wallet, receiver_wallet, amount_to_send: Decimal):
    with transaction.atomic():
        after_fee = amount_to_send + (amount_to_send * Decimal('0.01')
        if sender_wallet.balance < after_fee:
            raise ValueError("Insufficient balance")
            
        receiver_wallet.balance += amount_to_send
        sender_wallet.balance -= after_fee
        sender_wallet.save()
        receiver_wallet.save()
        TransactionModel.objects.create(
            sender=sender_wallet,
            receiver=receiver_wallet,
            sent=after_fee,
            received=amount_to_send,
            fee=amount_to_send * Decimal('0.01'),
            status='OK',
        )
        return True