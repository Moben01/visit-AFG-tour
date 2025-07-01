from django.shortcuts import render
from django.utils.translation import *
from tour.models import *

# Create your views here.
def home_view(request):
    get_tour_categories = TourCategory.objects.all()
    get_main_things = Main_things.objects.last()
    user_id = request.user.id
    find_user = User.objects.get(id=user_id)
    find_user_favorite = User_favorite_tour.objects.filter(user=find_user, favorite=True).count()

    language_code = get_language()

    if language_code == 'fa' or language_code == "ar":
            # Do something for right-to-left languages
        return render(request, 'RTL/index.html')
    else:
        return render(request, 'index.html', {'get_tour_categories':get_tour_categories, 'find_user_favorite':find_user_favorite, 'get_main_things':get_main_things})
