from django.urls import path
from . import views

app_name = 'things_to_do'  # ✅ This is required for namespacing

urlpatterns = [
    path('Art_and_Culture/', views.Art_and_Culture, name='Art_and_Culture'),  # example
]