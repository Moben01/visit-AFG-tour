from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from tour.models import *
from tour.forms import *
from django.contrib import messages
from django.http import HttpResponse
import stripe
from decimal import Decimal
from django.conf import settings
import json
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
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


def tour_booking(request, slug):
    selected_accommodation = None
    selected_transport = None

    find_tour = Tour.objects.get(slug=slug)
    get_interary = ItineraryItem.objects.filter(tour=find_tour)
    get_tour_categories = TourCategory.objects.all()
    accommodation = Accommodation.objects.all()
    transport = Transport.objects.all()
    languages_ = Languages.objects.all()
    security_guards = SecurityGuard.objects.all()

    # Get selected transport and accommodation from itinerary items
    selected_transports = set(item.transport for item in get_interary if item.transport)
    selected_accommodations = set(item.accommodation for item in get_interary if item.accommodation)

    # Calculate total price
    total_transport_price = sum(t.total_price for t in selected_transports)
    total_accommodation_price = sum(a.total_price for a in selected_accommodations)

    total_price = Decimal(total_transport_price) + Decimal(total_accommodation_price)

    if request.method == 'POST' and request.htmx:
        accommodation_id = request.POST.get('selected_accommodation')
        transport_id = request.POST.get('selected_transport')
        selected_languages = request.POST.getlist('language[]')  # This returns a list of all selected values (lang.code)
        security_gard = request.POST.get('security')  # returns 'on' if checked, or None if not

        # Here we reset total price, **only add newly selected items prices**
        total_price = Decimal('0')

        if accommodation_id:
            selected_accommodation = get_object_or_404(Accommodation, id=accommodation_id)
            total_price += Decimal(selected_accommodation.total_price)

        if transport_id:
            selected_transport = get_object_or_404(Transport, id=transport_id)
            total_price += Decimal(selected_transport.total_price)

        selected_language_objs = []

        if selected_languages:
            selected_language_objs = Languages.objects.filter(code__in=selected_languages)
            total_price += sum((Decimal(lang.total_price) for lang in selected_language_objs), Decimal('0'))
        else:
            selected_languages = None
        
        # ✅ SECURITY GUARD LOGIC
        if security_gard and selected_language_objs:
            from django.db.models import Count, Q

            find_security_guard = (
                SecurityGuard.objects
                .annotate(match_count=Count('languages', filter=Q(languages__in=selected_language_objs), distinct=True))
                .filter(match_count=selected_language_objs.count())
                .last()
            )

            if find_security_guard:
                total_price += Decimal(find_security_guard.total_price)
        else:
            security_gard = None


        return render(request, 'partials/tour/_total_price_button.html', {
            'total_price': total_price,
        })

    request.session['totalprice'] = float(total_price)

    context = {
        'get_tour_categories':get_tour_categories,
        'find_tour':find_tour,
        'get_interary':get_interary,
        'accommodation':accommodation,
        'transport':transport,
        'selected_accommodation':selected_accommodation,
        'total_price':total_price,
        'languages_':languages_,
        'security_guards':security_guards,
        'selected_transports': selected_transports,
        'selected_accommodations': selected_accommodations,
    }
    
    return render(request, 'tour/tour-booking.html', context)


def translator_view(request):
    message = ""  # پیام خالی در ابتدا
    form = TranslatorForm()

    if request.method == 'POST':
        form = TranslatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            message = "Your information has been successfully registered."
            return redirect('home:home')  # create a success page


    context = {
        'form': form,
        'message': message,
        'get_tour_categories': TourCategory.objects.all() 
    }
    return render(request, 'tour_involve/translator.html', context)




def tour_guide_view(request):
    message = ""  # پیام خالی در ابتدا

    if request.method == 'POST':
        form = TourGuideForm(request.POST, request.FILES)
        if form.is_valid():
            tour_guide = form.save(commit=False)
            tour_guide.is_approved = False  # Require admin approval
            tour_guide.save()
            message = "Your information has been successfully registered."

            return redirect('home:home')  # create a success page
    else:
        form = TourGuideForm()
    context = {
        'form': form,
        'message': message,
        'get_tour_categories': TourCategory.objects.all() 
    }
    return render(request, 'tour_involve/tour_guide.html', context)






@login_required
def tg_doc_dashboard(request):
    user = request.user

    # Example context data
    context = {
        'username': user.username,
        'email': user.email,
        'last_login': user.last_login,
        'date_joined': user.date_joined,
        'notifications': ['Welcome to your dashboard!', 'New message from support.'],
        'recent_activities': [
            'Logged in today',
            'Updated profile info',
            'Viewed product XYZ'
        ]
    }
    return render(request, 'tour_involve/tg_dashboard.html', context)



@login_required
def user_newsfeed(request):
    user = request.user
    user_type = user.my_choice_field  # Accessing the custom field

    all_tours_assignment = TourGuideAssignment.objects.filter(status=True)

    context = {
        'all_tours_assignment': all_tours_assignment,
    }

    # Conditionally render different templates based on user type
    if user_type == 'Tourist':
        return render(request, 'tour/tourist_newsfeed.html', context)
    elif user_type == 'Guide':
        return render(request, 'tour_involve/guide_newsfeed.html', context)
    else:
        return render(request, 'tour_involve/tg_doc_newsfeed.html', context)
    


@login_required
def payment(request):
    selected_accommodation = request.session.get('totalprice', None)

    html_content = f"""
    <html>
      <head>
        <style>
          /* Spinner CSS */
          .spinner {{
            margin: 20px auto;
            width: 40px;
            height: 40px;
            border: 4px solid #ccc;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }}

          @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
          }}

          .message {{
            font-family: Arial, sans-serif;
            font-size: 18px;
            text-align: center;
            margin-top: 20px;
            color: #333;
          }}
        </style>
      </head>
      <body>
        <div class="message">Payment Is In Processing .... {selected_accommodation}</div>
        <div class="spinner"></div>
      </body>
    </html>
    """

    return HttpResponse(html_content)




@login_required
def up_commoing_tours(request):
    user = request.user
    user_type = user.my_choice_field  # Accessing the custom field

    upcomming_tours = Booking.objects.filter(situation='upcoming', user=user)

    context = {
        'upcomming_tours': upcomming_tours,
    }

    # Conditionally render different templates based on user type
    return render(request, 'tour/upcomming_tours/tourist_upcomming_tour.html', context)
    
    




@login_required
def up_commoing_tours_more_info(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    edit_mode = request.GET.get('edit') == '1'

    # Ensure 0..1 object per booking
    pre_arrival = PreArrivalRequirement.objects.filter(booking=booking).first()

    # When not editing and a record exists: hide form
    show_form = edit_mode or (pre_arrival is None)

    form = PreArrivalRequirementForm(
        request.POST or None,
        request.FILES or None,
        instance=pre_arrival
    )

    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')

    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.booking = booking

                # Optionally: clear fields based on visa_status like we set earlier
                status = instance.visa_status
                if status == 'yes':
                    instance.passport_copy = None
                    instance.travel_start_date = None
                    instance.travel_end_date = None
                    instance.embassy_location = ''
                    instance.emergency_contact_name = ''
                    instance.emergency_contact_phone = ''
                    instance.emergency_contact_email = None
                    instance.has_insurance = False
                    instance.insurance_copy = None
                    instance.has_medical_conditions = False
                    instance.medical_notes = ''
                    instance.needs_afghan_sim = False
                    instance.safety_guideline_accepted = False
                elif status == 'no':
                    if instance.visa_copy:
                        try:
                            instance.visa_copy.delete(save=False)
                        except Exception:
                            pass
                        instance.visa_copy = None

                instance.save()

            messages.success(request, "Your pre-arrival information was saved.")
            # Redirect WITHOUT ?edit=1 so the form is hidden after save
            return redirect('tour:up_commoing_tours_more_info', id=booking.id)

        messages.error(request, "Please fix the errors below.")

    context = {
        'form': form,
        'booking': booking,
        'pre_arrival': pre_arrival,
        'show_form': show_form,
        'itinerary_items': itinerary_items,
    }
    return render(request, 'tour/upcomming_tours/tourist_upcomming_tour_details.html', context)




@login_required
def pre_arrival_form(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')



    # One-to-one: either edit existing or create new
    instance = getattr(booking, 'pre_arrival', None)

    if request.method == 'POST':
        form = PreArrivalForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.booking = booking
            obj.save()

            return redirect('tour:pre_arrival_form', id=booking.id)
    else:
        form = PreArrivalForm(instance=instance)

    return render(request, 'tour/upcomming_tours/tourist_pre_arrival_info.html', {
        'form': form,
        'booking': booking,
        'instance': instance,
        'itinerary_items':itinerary_items,
    })




@login_required
def pickup_plan_edit(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    instance = getattr(booking, 'pickup', None)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')


    if request.method == 'POST':
        form = PickupPlanForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.booking = booking
            # tip: prefill from pre_arrival if empty
            if not obj.entry_point_code and hasattr(booking, 'pre_arrival'):
                obj.entry_point_code = booking.pre_arrival.entry_point
                obj.entry_point_label = booking.pre_arrival.get_entry_point_display()
            obj.save()
            return redirect('pickup_plan_detail', booking_id=booking.id)
    else:
        form = PickupPlanForm(instance=instance)

    return render(request, 'tour/upcomming_tours/tourist_arrival_pickup.html', {
        'booking': booking, 'form': form, 'instance': instance, 'itinerary_items':itinerary_items,
    })

@login_required
def pickup_plan_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')

    pickup = getattr(booking, 'pickup', None)
    return render(request, 'tour/upcomming_tours/tourist_arrival_pickup.html', {
        'booking': booking, 'pickup': pickup, 'itinerary_items':itinerary_items,
    })


@login_required
@require_POST
def pickup_update_status(request, booking_id):
    pickup = get_object_or_404(PickupPlan, booking_id=booking_id)
    new_status = request.POST.get('status')
    if new_status in dict(PickupPlan.STATUS):
        pickup.status = new_status
        if new_status == 'picked_up':
            pickup.mark_picked_up()
        else:
            pickup.save(update_fields=['status','updated_at'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))



@login_required
def welcome_package_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')


    # Restrict access so only the booking owner or staff can view
    if request.user != booking.user and not request.user.is_staff:
        return render(request, "403.html", status=403)

    package = getattr(booking, 'welcome_package', None)

    # For an elegant empty state
    gifts = package.gifts.all() if package else []

    return render(request, "tour/upcomming_tours/tourist_wellcom_package.html", {
        "booking": booking,
        "package": package,
        "gifts": gifts,
        'itinerary_items':itinerary_items,
    })



def itenary_full_info(request, id, booking_id ):
    booking = get_object_or_404(Booking, id=booking_id)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')

    item_id = id

    item = get_object_or_404(
        ItineraryItem.objects.select_related(
            "tour", "accommodation", "transport", "tour_guide", "meals", "logistics"
        ),
        id=item_id,
    )

    # Prev / Next within the same tour by day_number
    prev_item = (
        ItineraryItem.objects
        .filter(tour=item.tour, day_number__lt=item.day_number)
        .order_by("-day_number")
        .first()
    )
    next_item = (
        ItineraryItem.objects
        .filter(tour=item.tour, day_number__gt=item.day_number)
        .order_by("day_number")
        .first()
    )

    return render(request, "tour/upcomming_tours/tourist_itenary_info.html", {
        "item": item,
        "prev_item": prev_item,
        "next_item": next_item,
        "booking": booking,
        'itinerary_items':itinerary_items,

    })