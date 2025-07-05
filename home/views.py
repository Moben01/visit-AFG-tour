from django.shortcuts import render
from django.utils.translation import *
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import get_language
from tour.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import*

# Create your views here.
def home_view(request):
    get_tour_categories = TourCategory.objects.all()
    get_main_things = Main_things.objects.last()
    if get_main_things is None:
        # handle the empty case, e.g. set defaults or skip
        pass
    user_id = request.user.id
    find_user = User.objects.get(id=user_id)
    find_user_favorite = User_favorite_tour.objects.filter(user=find_user, favorite=True).count()
    find_user_favorite = 0  # Default for anonymous users

    if request.user.is_authenticated:
        try:
            find_user = User.objects.get(id=request.user.id)
            find_user_favorite = User_favorite_tour.objects.filter(user=find_user, favorite=True).count()
        except User.DoesNotExist:
            find_user_favorite = 0  # fallback if user not found for some reason

    language_code = get_language()

    if language_code in ['fa', 'ar']:
        return render(request, 'RTL/index.html')
    else:
        return render(request, 'index.html', {'get_tour_categories':get_tour_categories, 'find_user_favorite':find_user_favorite, 'get_main_things':get_main_things})
        return render(request,'index.html',{'get_tour_categories': get_tour_categories,'find_user_favorite': find_user_favorite})


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


@login_required  # better than manual check for logged-in user
def favorite_user_tour(request):
    get_tour_categories = TourCategory.objects.all()

    if request.method == "POST":
        slug = request.POST.get('slug')  # get the slug from POST data

        # If slug is missing, you might want to handle that gracefully
        if not slug:
            # You could add a message or redirect
            return redirect('some_view_name')  

        tour = get_object_or_404(Tour, slug=slug)

        # Get or create favorite object
        favorite, created = User_favorite_tour.objects.get_or_create(user=request.user, tour=tour)

        # Toggle the favorite boolean
        favorite.favorite = not favorite.favorite
        favorite.save()

    # Fetch the current user's favorites marked True
    find_user_favorites = User_favorite_tour.objects.filter(user=request.user, favorite=True)
    find_user_favorite = find_user_favorites.count()

    context = {
        'find_user_favorite': find_user_favorite,
        'get_tour_categories': get_tour_categories,
        'find_user_favorites': find_user_favorites,
    }

    return render(request, 'home/user-wish-list.html', context)
