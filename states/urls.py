from django.urls import path
from .import views


app_name = 'home'

urlpatterns = [
    path('kabul', views.kabul, name='kabul'),
    path('balkh', views.balkh, name='balkh'),
    path('samangan', views.samangan, name='samangan'),
    path('jawzjan', views.jawzjan, name='jawzjan'),
    path('faryab', views.faryab, name='faryab'),
    path('SarePol', views.SarePol, name='SarePol'),
    path('Baghlan', views.Baghlan, name='Baghlan'),
    path('Kunduz', views.Kunduz, name='Kunduz'),
    path('Takhar', views.Takhar, name='Takhar'),
    path('Badakhshan', views.Badakhshan, name='Badakhshan'),
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
    path('Nangarhar', views.Nangarhar, name='Nangarhar'),
    path('Kunar', views.Kunar, name='Kunar'),
    path('Laghman', views.Laghman, name='Laghman'),
    path('Nuristan', views.Nuristan, name='Nuristan'),

    path('Kandahar', views.Kandahar, name='Kandahar'),

    path('Helmand', views.Helmand, name='Helmand'),
    path('Zabul', views.Zabul, name='Zabul'),
    
    
    path('Herat', views.Herat, name='Herat'),
    path('Farah', views.Farah, name='Farah'),
    path('Badghis', views.Badghis, name='Badghis'),
    path('Ghor', views.Ghor, name='Ghor'),
]