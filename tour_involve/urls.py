from django.urls import path
from . import views









app_name = 'tour_involve' 

urlpatterns = [
    path('translator_view/', views.translator_view, name='translator_view'), 
   
]