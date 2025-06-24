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
    path('Badakhshan', views.Badakhshan, name='Badakhshan')
]