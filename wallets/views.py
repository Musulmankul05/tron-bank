from cryptography.fernet import Fernet
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import pyotp

from users.models import KYCModel
from wallets.models import CardModel

# Create your views here.
class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated and not getattr(request.user, 'totp_secret', None):
            return redirect('users:setup2fa')
        return render(request, 'index.html')

class AccountView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'cards': CardModel.objects.filter(owner=request.user)
        }
        return render(request, 'account.html', context=context)

class NewCardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'create.html')

    def post(self, request):
        name = request.POST.get('name')
        currency = request.POST.get('currency')
        user_2fa = request.POST.get('otp_code')
        totp = pyotp.TOTP(request.user.totp_secret)

        if not user_2fa:
            return render(request, 'create.html', {'error': '2FA is required'})
        if totp.verify(user_2fa):
            CardModel.objects.create(owner=request.user, name=name, currency=currency)
            return redirect('wallets:account')
        else:
            return render(request, 'create.html', {'error': 'Invalid 2FA code'})

class ReceiptView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            kyc = KYCModel.objects.get(user=request.user)
            encrypted_signature = kyc.signature_svg
        except KYCModel.DoesNotExist:
            kyc = None
            encrypted_signature = None

        decrypted_signature = None

        if encrypted_signature:
            try:
                print(settings.SIGNATURE_CRYPTO_KEY.encode('utf-8'))
                cipher = Fernet(settings.SIGNATURE_CRYPTO_KEY.encode('utf-8'))

                decrypted_signature = cipher.decrypt(encrypted_signature.encode('utf-8')).decode('utf-8')
            except Exception as e:
                decrypted_signature = 'error'
                print(e)

        context = {
            'kyc': kyc,
            'signature_base64': decrypted_signature
        }
        return render(request, 'receipt.html', context)


        