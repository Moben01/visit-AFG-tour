from django.urls import path
from . import views

app_name = 'things_to_do' 

urlpatterns = [
    path('Art_and_Culture/', views.Art_and_Culture, name='Art_and_Culture'), 
    path('Experiences/', views.Experiences, name='Experiences'), 
    path('food_and_drink/', views.food_and_drink, name='food_and_drink'), 
    path('New_and_Trending/', views.New_and_Trending, name='New_and_Trending'),
    path('wellness-in-dubai/', views.wellness_in_dubai, name='wellness_in_dubai'),
    path('Itineraries/', views.Itineraries, name='Itineraries'),
]