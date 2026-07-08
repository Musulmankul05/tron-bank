from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q
from .services import execute_transfer
from decimal import Decimal
from users.models import UserModel
from wallets.models import CardModel

# Create your views here.
class TransferView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'transfer.html', context={'cards': CardModel.objects.filter(owner=request.user)})

    def post(self, request):
        card_id = request.POST.get('card')
        receiver_data = request.POST.get('receiver')
        amount = Decimal(request.POST.get('amount'))

        if not card_id or not receiver_data or not amount:
            return render(request, 'transfer.html', {'error': 'All fields are required'})
        print("all fields are non-empty.")

        receiver_data = receiver_data.strip().lstrip('@')
        print(receiver_data)

        card = CardModel.objects.filter(owner=request.user, pk=card_id).first()
        if not card:
            return render(request, 'transfer.html', {'error': 'Card not found or access denied', 'cards': CardModel.objects.filter(owner=request.user)})
        
        try:
            receiver = UserModel.objects.get(Q(phone=receiver_data) | Q(username=receiver_data))
        except UserModel.DoesNotExist:
            return render(request, 'transfer.html', {'error': 'Receiver not found', 'cards': CardModel.objects.filter(owner=request.user)})

        receiver_card = CardModel.objects.filter(owner=receiver, currency = card.currency).first()
        print(f'To Card: {receiver_card}\nFrom Card: {card}')
        
        if not receiver_card:
            return render(request, 'transfer.html', {'error': 'Receiver not found', 'cards': CardModel.objects.filter(owner=request.user)})
        
        try:
            execute_transfer(card, receiver_card, amount)
            print('execute_transfer successful')
            return render(request, 'transfer.html', {'success': 'Transfer successful', 'cards': CardModel.objects.filter(owner=request.user)})
        except Exception as e:
            print(e)
            return render(request, 'transfer.html', {'error': str(e)})