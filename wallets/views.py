from cryptography.fernet import Fernet
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View

from users.models import KYCModel

# Create your views here.
class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated and not getattr(request.user, 'totp_secret', None):
            return redirect('users:setup2fa')
        return render(request, 'index.html')

class AccountView(View):
    def get(self, request):
        return render(request, 'account.html')

class ReceiptView(View):
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
                