from django.urls import path
from . import views

namespace = 'wallets'

urlpatterns = [
    path('', views.index_view, name='index')
]