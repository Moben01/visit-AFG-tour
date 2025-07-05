from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from tour.models import *
from tour.forms import *
from django.contrib import messages
from django.http import HttpResponse
import stripe
from django.conf import settings
import json
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY
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

from django.template.loader import render_to_string
from django.http import HttpResponse

@login_required
def toggle_favorite(request, slug):
    tour = get_object_or_404(Tour, slug=slug)
    favorite, _ = User_favorite_tour.objects.get_or_create(user=request.user, tour=tour)

    favorite.favorite = not favorite.favorite
    favorite.save()

    is_favorite = favorite.favorite

    html = render_to_string("tour/partials/favorite_button.html", {
        "get_tour": tour,
        "is_favorite": is_favorite
    }, request=request)

    return HttpResponse(html)



def tour_details(request, slug):

    find_user_favorite = 0  # default value

    if request.user.is_authenticated:
        try:
            find_user = User.objects.get(id=request.user.id)
            find_user_favorite = User_favorite_tour.objects.filter(user=find_user, favorite=True).count()
        except User.DoesNotExist:
            pass

    get_tour = Tour.objects.get(slug=slug)
    get_EnquireUs = EnquireUs.objects.filter(tour=get_tour)

    if request.htmx and request.method == 'POST':
        print('re is htmx')
        form = EnquireUsForm(request.POST)
        if form.is_valid():
            print('form is valid')
            instance = form.save(commit=False)

            instance.tour = get_tour
            instance.save()
            messages.success(request, "Your enquiry has been submitted successfully!")
            return render(request, 'tour/partials/endquires_list.html', 
            {
            'get_EnquireUs':get_EnquireUs,
            'form': EnquireUsForm(),
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        print('req is not htmx')
        form = EnquireUsForm()

    get_tour_categories = TourCategory.objects.all()
    tour_images = get_tour.images.all()  # related_name = 'images'
    find_Itinerary = ItineraryItem.objects.filter(tour=get_tour)
    get_faqs = Frequently_asked_questions.objects.filter(tour_id=get_tour)
    Includess = Includes.objects.filter(tour=get_tour)
    Excludess = Excludes.objects.filter(tour=get_tour)
    pub_key = settings.STRIPE_PUBLIC_KEY 

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
        'pub_key':pub_key,
    }
    return render(request, 'tour/tour-details.html', context)

@login_required
def tour_booking(request, slug):
    find_tour = Tour.objects.get(slug=slug)

    # ✅ Always delete old "ready to book" records for this user
    Ready_tour_for_booking.objects.filter(user=request.user).delete()

    # ✅ Then create a new one for the selected tour
    Ready_tour_for_booking.objects.create(
        tour=find_tour,
        user=request.user
    )
    user_id = request.user.id
    find_user = User.objects.get(id=user_id)
    cart = Ready_tour_for_booking.objects.filter(user=find_user)
    total_price = 0

    items = []


    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.tour = find_tour
            instance.user = find_user
            for item in cart:
                product = item.tour  # product is Tour instance
                total_price += int(product.price * 100)  # convert to cents for Stripe

                items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.title,  # usually Tour uses title, not name
                            'images': [request.build_absolute_uri(product.image.url)],  # must be publicly accessible HTTPS URL
                        },
                        'unit_amount': int(product.price * 100),  # Stripe expects amount in cents as int
                    },
                    'quantity': 1,
                })

            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=items,
                mode='payment',
                success_url='http://127.0.0.1:8000/cart/success/',
                cancel_url='http://127.0.0.1:8000/cart/'
            )
            instance.save()
            return redirect(session.url, code=303)  # 303 redirect to Stripe checkout
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