from django.urls import path
from .import views
from home.views import favorite_user_tour

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='home'),

]

