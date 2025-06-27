from django.urls import path
from .import views


app_name = 'plan_your_trip'

urlpatterns = [
    path('visa_guide', views.visa_guide, name="visa_guide")
]