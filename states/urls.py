from django.urls import path
from .import views

app_name = 'home'

urlpatterns = [
    path('kabul', views.kabul, name='kabul'),
    path('parwan', views.parwan, name='parwan'),
    path('maidan_wardak', views.maidan_wardak, name='maidan_wardak'),
    path('Nangarhar', views.Nangarhar, name='Nangarhar'),
    path('Kunar', views.Kunar, name='Kunar'),
    path('Laghman', views.Laghman, name='Laghman'),
    path('Nuristan', views.Nuristan, name='Nuristan'),

    path('Kandahar', views.Kandahar, name='Kandahar'),
]