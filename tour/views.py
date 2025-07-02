from django.shortcuts import render
from tour.models import *

# Create your views here.

def tour_category_list(request, slug):
    get_tour_categories = TourCategory.objects.all()
    get_tour_category = TourCategory.objects.get(slug=slug)
    find_tours = Tour.objects.filter(category=get_tour_category)
    selected_types = request.GET.getlist('types')
    if selected_types:
        find_tours = Tour.objects.filter(category__id__in=selected_types)

    context = {
        'get_tour_category': get_tour_category,
        'find_tours': find_tours,
        'get_tour_categories': get_tour_categories,
        'selected_types': list(map(int, selected_types)) if selected_types else [],
    }
    return render(request, 'tour/tour-list.html', context)


def tour_details(request, slug):
    get_tour_categories = TourCategory.objects.all()
    get_tour = Tour.objects.get(slug=slug)
    tour_images = get_tour.images.all()  # related_name = 'images'
    find_Itinerary = ItineraryItem.objects.filter(tour=get_tour)
    get_faqs = Frequently_asked_questions.objects.filter(tour_id=get_tour)
    Includess = Includes.objects.filter(tour=get_tour)
    Excludess = Excludes.objects.filter(tour=get_tour)



    context = {
        'get_tour':get_tour,
        'tour_images':tour_images,
        'find_Itinerary':find_Itinerary,
        'get_tour_categories':get_tour_categories,
        'get_faqs':get_faqs,
        'Includess':Includess,
        'Excludess':Excludess,
    }
    return render(request, 'tour/tour-details.html', context)