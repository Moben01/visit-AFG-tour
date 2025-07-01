from django.urls import path
from . import views

app_name = 'tour' 

urlpatterns = [
   path('tours/<slug:slug>/', views.tour_category_list, name='tour_category_list'),
   path('tour-detail/<slug:slug>/', views.tour_details, name='tour_details'),
   path('tour/<slug:slug>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]