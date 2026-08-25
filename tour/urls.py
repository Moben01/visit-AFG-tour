from django.urls import include, path
from . import views
from . import resource_views

app_name = 'tour' 

urlpatterns = [
   path('tours/<slug:slug>/', views.tour_category_list, name='tour_category_list'),
   path('tour-detail/<slug:slug>/', views.tour_details, name='tour_details'),
   path('tour/<slug:slug>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
   path('tour/<slug:slug>/tour_booking/', views.tour_booking, name='tour_booking'),
   path('translator_view/', views.translator_view, name='translator_view'), 
   path('tour_guide_view/', views.tour_guide_view, name='tour_guide_view'), 
   path('operations/', include('tour.operations_urls', namespace='operations')),
   path('crew/', include('tour.crew_urls', namespace='crew')),
   path('supplier/', include('tour.supplier_urls', namespace='supplier')),
   path('dashboard/', views.dashboard_router, name='dashboard'),
   path('agent/dashboard/', views.tg_doc_dashboard, name='tg_doc_dashboard'),
   path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
   path('user_newsfeed/', views.user_newsfeed, name='user_newsfeed'),
   path('payment/', views.payment, name='payment_legacy'),
   path('payment/<int:booking_id>/', views.payment, name='payment'),
   path('payment/<int:booking_id>/checkout/', views.create_checkout_session, name='create_checkout_session'),
   path('payment/<int:booking_id>/success/', views.payment_success, name='payment_success'),
   path('payment/<int:booking_id>/cancel/', views.payment_cancel, name='payment_cancel'),
   path('payment/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),

   path('up_commoing_tours/', views.up_commoing_tours, name='up_commoing_tours'),
   path('customer/tours/', views.customer_tours, name='customer_tours'),
   path('up_commoing_tours_more_info/<int:id>/', views.up_commoing_tours_more_info, name='up_commoing_tours_more_info'),
   path('pre-arrival/<int:id>/', views.pre_arrival_form, name='pre_arrival_form'),
   path('pickup/<int:booking_id>/', views.pickup_plan_detail, name='pickup_plan_detail'),
   path('pickup/<int:booking_id>/edit/', views.pickup_plan_edit, name='pickup_plan_edit'),
   path('pickup/<int:booking_id>/status/', views.pickup_update_status, name='pickup_update_status'),
   path("welcome-package/<int:booking_id>/", views.welcome_package_detail, name="welcome_package_detail"),

   path('itenary_full_info/<int:id>/<int:booking_id>', views.itenary_full_info, name='itenary_full_info'),
   path('edit_itinerary/<int:itienary_id>/<int:user_id>', views.edit_itinerary, name='edit_itinerary'),
   path('crew-review/<int:engagement_id>/', resource_views.customer_crew_review, name='customer_crew_review'),

]
