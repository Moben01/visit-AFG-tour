from django.shortcuts import render, redirect
from tour.models import *
from tour.forms import *
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.

def tour_category_list(request, slug):
    get_tour_categories = TourCategory.objects.all()
    get_tour_category = TourCategory.objects.get(slug=slug)
    find_tours = Tour.objects.filter(category=get_tour_category)

    context = {
        'get_tour_category':get_tour_category,
        'find_tours':find_tours,
        'get_tour_categories':get_tour_categories,
    }
    return render(request, 'tour/tour-list.html', context)

def tour_details(request, slug):
    get_tour = Tour.objects.get(slug=slug)
    if request.method == 'POST':
        form = EnquireUsForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.tour = get_tour
            instance.save()
            messages.success(request, 'Your enquiry has been submitted successfully.')
            return redirect('tour:tour_details', slug=instance.tour.slug)  # Adjust to your URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EnquireUsForm()

    get_tour_categories = TourCategory.objects.all()
    tour_images = get_tour.images.all()  # related_name = 'images'
    find_Itinerary = ItineraryItem.objects.filter(tour=get_tour)
    get_EnquireUs = EnquireUs.objects.filter(tour=get_tour)
    get_faqs = Frequently_asked_questions.objects.filter(tour_id=get_tour)

    context = {
        'get_tour':get_tour,
        'tour_images':tour_images,
        'find_Itinerary':find_Itinerary,
        'get_tour_categories':get_tour_categories,
        'get_faqs':get_faqs,
        'form':form,
        'get_EnquireUs':get_EnquireUs,
    }
    return render(request, 'tour/tour-details.html', context)