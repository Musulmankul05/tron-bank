from django.db import transaction
from transactions.models import TransactionModel
from decimal import Decimal

def execute_transfer(sender_wallet, receiver_wallet, amount_to_send: Decimal):
    if amount_to_send <= Decimal('0'):
            raise ValueError("Amount must be greater than zero")
            
    with transaction.atomic():
        sender = sender_wallet.__class__.objects.select_for_update().get(pk=sender_wallet.pk)
        receiver = receiver_wallet.__class__.objects.select_for_update().get(pk=receiver_wallet.pk)
        
        after_fee = amount_to_send + (amount_to_send * Decimal('0.012'))
        if sender.balance < after_fee:
            raise ValueError("Insufficient balance")
            
        receiver.balance += amount_to_send
        sender.balance -= after_fee
        
        sender.save(update_fields=['balance'])
        receiver.save(update_fields=['balance'])
        TransactionModel.objects.create(
            sender=sender,
            receiver=receiver,
            sent=after_fee,
            received=amount_to_send,
            fee=amount_to_send * Decimal('0.012'),
            status='OK',
        )
        return True