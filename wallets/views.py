from django.shortcuts import redirect, render
from django.views import View

# Create your views here.
class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated and not getattr(request.user, 'totp_secret', None):
            return redirect('users:setup2fa')
        return render(request, 'index.html')

class AccountView(View):
    def get(self, request):
        return render(request, 'account.html')