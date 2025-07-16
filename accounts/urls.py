from django.urls import path
from .import views

app_name = "accounts"

urlpatterns = [
    path('accounts/settings/', views.account_settings, name='account_settings')
]