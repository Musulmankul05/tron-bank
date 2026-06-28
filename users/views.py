from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout

def logout_view(request):
    logout(request)
    return redirect('wallets:index')

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
            login(request, user)
            return redirect('wallets:index')
        else:
            return render(request, 'login.html', {'error': 'Invalid phone number or password'})