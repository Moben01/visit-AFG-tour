from django.urls import path
from .import views

app_name = 'home'

urlpatterns = [
    path('kabul', views.kabul, name='kabul'),
    path('parwan', views.parwan, name='parwan'),
    path('maidan_wardak', views.maidan_wardak, name='maidan_wardak'),
    path('bamyan', views.bamyan, name='bamyan'),
    path('logar', views.logar, name='logar'),
    path('kapisa', views.kapisa, name='kapisa'),
    path('panjshir', views.panjshir, name='panjshir'),
    path('daikundi', views.daikundi, name='daikundi'),
    path('ghazni', views.ghazni, name='ghazni'),
    path('paktika', views.paktika, name='paktika'),
    path('khost', views.khost, name='khost'),
]