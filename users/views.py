from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.utils.crypto import get_random_string
from .models import BackupCodesModel
import hashlib
import pyotp
import time
import secrets

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
            request.session['allow_view_codes'] = True
            if 'pre_auth_user_id' in request.session:
                del request.session['pre_auth_user_id']
            return redirect('users:backup-codes')
        else:
            user.totp_secret = None
            user.save()
            return render(request, 'setup2fa.html', {'error': 'Invalid activation code. Try again.'})

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
            if not user.backups.exists():
                request.session['allow_view_codes'] = True
                return redirect('users:backup-codes')
            else:
                return redirect('wallets:index')
        else:
            return render(request, 'verify2fa.html', {'error': 'Invalid verification code'})

class BackupCodeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if request.user.backups.exists():
            return redirect('wallets:index')

        if not request.session.get('allow_view_codes', False):
            return redirect('wallets:index')
            
        del request.session['allow_view_codes']
        backup_tokens = []
        backups_array = []
        start = time.perf_counter()
        for _ in range(4):
            raw_code = f"{secrets.randbelow(9000)+1000}-{secrets.randbelow(9000)+1000}"
            backup_tokens.append(raw_code)

            hashed = hashlib.sha256(raw_code.encode()).hexdigest()
            
            backups_array.append(BackupCodesModel(
                user=request.user,
                code=hashed
            ))
        BackupCodesModel.objects.bulk_create(
            backups_array, update_conflicts=True, 
            unique_fields=['id'], update_fields=['user', 'code']
        )
        print(time.perf_counter() -start)
        request.session['codes_generated'] = True
        
        # Отдаем эти чистые raw_code юзеру на фронтенд только ОДИН раз, чтобы он их записал
        return render(request, 'backup_codes.html', {'codes': backup_tokens})

class BackupEnterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('wallets:index')
        if 'pre_auth_user_id' not in request.session:
            return redirect('users:login')
        return render(request, 'enter_backup_codes.html')

    def post(self, request):
        if 'pre_auth_user_id' not in request.session:
            return redirect('users:login')
        user_id = request.session['pre_auth_user_id']
        code = request.POST.get('otp_code', '').strip()
        if not code:
            return render(request, 'enter_backup_codes.html', {'error': 'Code is empty.'})
            
        hashed = hashlib.sha256(code.encode()).hexdigest()
        backup_entry = BackupCodesModel.objects.filter(
            user_id=user_id,
            code=hashed
        ).first()

        if backup_entry:
           backup_entry.delete()
           management_user = BackupCodesModel._meta.get_field('user').remote_field.model 
           user = management_user.objects.get(id=user_id)

           login(request, user, backend='users.backends.PhoneAuthBackend')
           request.user.backups.all().delete()
           request.user.totp_secret = None
           request.user.save()
           del request.session['pre_auth_user_id']
           return redirect('users:setup2fa')
        else:
            return render(request, 'enter_backup_codes.html', {'error': 'Incorrect code or already used.'})
        
def registration_view(request):
    return render(request, 'registration.html')