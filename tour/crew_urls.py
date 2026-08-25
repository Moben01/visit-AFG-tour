from django.urls import path

from . import resource_views as views

app_name = 'crew'

urlpatterns = [
    path('onboarding/', views.crew_onboarding, name='onboarding'),
    path('', views.crew_dashboard, name='dashboard'),
    path('profile/', views.crew_profile, name='profile'),
    path('profile/roles/add/', views.crew_qualification_add, name='qualification_add'),
    path('profile/documents/add/', views.crew_document_add, name='document_add'),
    path('profile/availability/add/', views.crew_availability_add, name='availability_add'),
    path('opportunities/', views.crew_opportunity_list, name='opportunities'),
    path('opportunities/<int:opportunity_id>/', views.crew_opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:opportunity_id>/apply/', views.crew_apply, name='apply'),
    path('applications/', views.crew_applications, name='applications'),
    path('offers/<int:offer_id>/', views.crew_offer_detail, name='offer_detail'),
    path('offers/<int:offer_id>/respond/', views.crew_offer_response, name='offer_response'),
    path('assignments/', views.crew_engagements, name='engagements'),
    path('assignments/<int:engagement_id>/', views.crew_engagement_detail, name='engagement_detail'),
    path('assignments/<int:engagement_id>/check-in/', views.crew_engagement_checkin, name='checkin'),
    path('assignments/<int:engagement_id>/check-out/', views.crew_engagement_checkout, name='checkout'),
    path('training/', views.crew_training, name='training'),
    path('support/', views.crew_cases, name='cases'),
    path('support/new/', views.crew_case_create, name='case_create'),
]
