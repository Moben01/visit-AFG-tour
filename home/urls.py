from django.urls import path
from .import views
from home.views import favorite_user_tour

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='home'),
    
  

]


from .urls_v2 import urlpatterns  # noqa: E402,F401
