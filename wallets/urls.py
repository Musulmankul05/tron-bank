from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('receipt/', views.ReceiptView.as_view(), name='receipt'),
    path('create/', views.NewCardView.as_view(), name='create'),
]