from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from tour.models import *
from tour.forms import *
from django.contrib import messages
from django.http import HttpResponse
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

@login_required
def toggle_favorite(request, slug):
    tour = get_object_or_404(Tour, slug=slug)
    favorite, created = User_favorite_tour.objects.get_or_create(user=request.user, tour=tour)

    favorite.favorite = not favorite.favorite
    favorite.save()

    return redirect('tour:tour_details', slug=slug)

def tour_details(request, slug):
    user_id = request.user.id
    find_user = User.objects.get(id=user_id)
    find_user_favorite = User_favorite_tour.objects.filter(user=find_user, favorite=True).count()

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
    Includess = Includes.objects.filter(tour=get_tour)
    Excludess = Excludes.objects.filter(tour=get_tour)



    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = User_favorite_tour.objects.filter(user=request.user, tour=get_tour, favorite=True).exists()

    context = {
        'get_tour':get_tour,
        'tour_images':tour_images,
        'find_Itinerary':find_Itinerary,
        'get_tour_categories':get_tour_categories,
        'get_faqs':get_faqs,
        'form':form,
        'get_EnquireUs':get_EnquireUs,
        'is_favorite': is_favorite,
        'find_user_favorite': find_user_favorite,
        'Includess':Includess,
        'Excludess':Excludess,
    }
    return render(request, 'tour/tour-details.html', context)

def tour_booking(request, slug):
    find_tour = Tour.objects.get(slug=slug)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.tour = find_tour
            instance.save()
        else:
            messages.warning(request, 'Form has Error')
    else:
        form = BookingForm()

    get_tour_categories = TourCategory.objects.all()

    context = {
        'get_tour_categories':get_tour_categories,
        'find_tour':find_tour,
        'form':form,
    }
    return render(request, 'tour/tour-booking.html', context)





from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import TranslatorForm
from tour.models import TourCategory
def translator_view(request):
    message = ""  # پیام خالی در ابتدا
    form = TranslatorForm()

    if request.method == 'POST':
        form = TranslatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            message = "The information has been successfully registered."

    context = {
        'form': form,
        'message': message,
        'get_tour_categories': TourCategory.objects.all() 
    }
    return render(request, 'tour_involve/translator.html', context)





