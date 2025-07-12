from django.urls import path
from . import views

app_name = 'tour' 

urlpatterns = [
   path('tours/<slug:slug>/', views.tour_category_list, name='tour_category_list'),
   path('tour-detail/<slug:slug>/', views.tour_details, name='tour_details'),
   path('tour/<slug:slug>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
   path('tour/<slug:slug>/tour_booking/', views.tour_booking, name='tour_booking'),
   path('translator_view/', views.translator_view, name='translator_view'), 
   path('tour_guide_view/', views.tour_guide_view, name='tour_guide_view'), 
   path('dashboard/', views.tg_doc_dashboard, name='tg_doc_dashboard'),
   path('user_newsfeed/', views.user_newsfeed, name='user_newsfeed'),
]