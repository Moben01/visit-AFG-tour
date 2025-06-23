from django.urls import path
from .import views

app_name = 'home'

urlpatterns = [
    path('kabul', views.kabul, name='kabul'),
    path('parwan', views.parwan, name='parwan'),
    path('maidan_wardak', views.maidan_wardak, name='maidan_wardak'),
    path('Kandahar', views.Kandahar, name='Kandahar'),
    path('Herat', views.Herat, name='Herat'),
    path('Farah', views.Farah, name='Farah'),
    path('Badghis', views.Badghis, name='Badghis'),
    path('Ghor', views.Ghor, name='Ghor'),
]