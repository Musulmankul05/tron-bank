from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('account/', views.AccountView.as_view(), name='account')
]