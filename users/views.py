from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
import pyotp

from users.models import UserModel

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('users:login')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        phone = request.POST.get('username')
        password = request.POST.get('password')

        if not phone or not password:
            return render(request, 'login.html', {'error': 'Fill in all fields.'})

        user = authenticate(request, username=phone, password=password)
        print(user, phone, password)

        if user is not None:
            request.session['pre_auth_user_id'] = user.id

            if not user.totp_secret:
                return redirect('users:setup2fa')
            else:
                return redirect('users:verify2fa')
                
        else:
            return render(request, 'login.html', {'error': 'Invalid phone number or password'})

class TwoFactorSetupView(View):
    def get(self, request):
        user_id = request.session.get('pre_auth_user_id')
        if not user_id:
            return redirect('users:login')

        user = UserModel.objects.get(id=user_id)

        if not user.totp_secret:
            user.totp_secret = pyotp.random_base32()
            user.save()

        totp_uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(
            issuer_name='tron'
        )
        return render(request, 'setup2fa.html', {'totp_uri': totp_uri})

    def post(self, request):
        user_id = request.session.get('pre_auth_user_id')
        otp_code = request.POST.get('otp_code')

        if not user_id or not otp_code:
            return redirect('users:login')

        user = UserModel.objects.get(id=user_id)
        totp = pyotp.TOTP(user.totp_secret)

        if totp.verify(otp_code):
            login(request, user, backend='users.backends.PhoneAuthBackend')
            del request.session['pre_auth_user_id']
            return redirect('wallets:index')
        else:
            user.totp_secret = None
            user.save()
            return redirect(request, 'setup2fa.html', {'error': 'Invalid activation code. Try again.'})

class TwoFactorVerifyView(View):
    def get(self, request):
        if not request.session.get('pre_auth_user_id'):
            return redirect('users:login')
        return render(request, 'verify2fa.html')

    def post(self, request):
        user_id = request.session.get('pre_auth_user_id')
        otp_code = request.POST.get('otp_code')

        if not user_id or not otp_code:
            return redirect('users:login')

        user = UserModel.objects.get(id=user_id)
        totp = pyotp.TOTP(user.totp_secret)

        if totp.verify(otp_code):
            login(request, user, backend='users.backends.PhoneAuthBackend')
            del request.session['pre_auth_user_id']
            return redirect('wallets:index')
        else:
            return render(request, 'verify2fa.html', {'error': 'Invalid verification code'})