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
   path('payment/', views.payment, name='payment'),

   path('up_commoing_tours/', views.up_commoing_tours, name='up_commoing_tours'),
   path('up_commoing_tours_more_info/<int:id>/', views.up_commoing_tours_more_info, name='up_commoing_tours_more_info'),
   path('pre-arrival/<int:id>/', views.pre_arrival_form, name='pre_arrival_form'),
   path('pickup/<int:booking_id>/', views.pickup_plan_detail, name='pickup_plan_detail'),
   path('pickup/<int:booking_id>/edit/', views.pickup_plan_edit, name='pickup_plan_edit'),
   path('pickup/<int:booking_id>/status/', views.pickup_update_status, name='pickup_update_status'),
   path("welcome-package/<int:booking_id>/", views.welcome_package_detail, name="welcome_package_detail"),

   path('itenary_full_info/<int:id>/<int:booking_id>', views.itenary_full_info, name='itenary_full_info'),
   path('edit_itinerary/<int:itienary_id>/<int:user_id>', views.edit_itinerary, name='edit_itinerary'),

]