
import requests
from django.shortcuts import render
import os
from dotenv import load_dotenv
load_dotenv()
from tour.models import *
import requests
from django.shortcuts import render

import requests
from django.shortcuts import render

def Art_and_Culture(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'things_to_do/Art_and_Culture.html', {'get_tour_categories':get_tour_categories})









def Experiences(request):
    get_tour_categories = TourCategory.objects.all()
    return render(request, 'things_to_do/Experiences.html',{'get_tour_categories':get_tour_categories})


def food_and_drink(request):
    get_tour_categories = TourCategory.objects.all()
    return render(request, 'things_to_do/food_and_drink.html',{'get_tour_categories':get_tour_categories})

def New_and_Trending(request):
    get_tour_categories = TourCategory.objects.all()
    return render(request, 'things_to_do/New_and_Trending.html',{'get_tour_categories':get_tour_categories})




def wellness_in_afg(request):
    get_tour_categories = TourCategory.objects.all()
    return render(request, 'things_to_do/wellness_in_dubai.html', {'get_tour_categories':get_tour_categories})




def Shopping(request):
    get_tour_categories = TourCategory.objects.all()
    return render(request, 'things_to_do/Shopping.html',{'get_tour_categories':get_tour_categories})

def Sights_(request):
    get_tour_categories = TourCategory.objects.all()
    return render(request, 'things_to_do/Sights_.html',{'get_tour_categories':get_tour_categories})
