from django.urls import path
from django.conf import settings
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/s2fa/', views.TwoFactorSetupView.as_view(), name='setup2fa'),
    path('login/v2fa/', views.TwoFactorVerifyView.as_view(), name='verify2fa'),
    path('registration/', views.registration_view, name='registration'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]