from django.urls import path
from .import views

app_name = 'home'

urlpatterns = [
    path('kabul', views.kabul, name='kabul'),
    path('parwan', views.parwan, name='parwan'),
    path('maidan_wardak', views.maidan_wardak, name='maidan_wardak'),
    path('Kandahar', views.Kandahar, name='Kandahar'),

    path('Helmand', views.Helmand, name='Helmand'),
    path('Zabul', views.Zabul, name='Zabul'),
    
    
]