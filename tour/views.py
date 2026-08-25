from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from tour.models import *
from tour.forms import *
from django.contrib import messages
from django.http import HttpResponse
import stripe
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
import json
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Sum
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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

@login_required
def tour_booking(request, slug):
    find_tour = get_object_or_404(Tour, slug=slug, available=True)
    user = request.user
    accommodation = Accommodation.objects.all().order_by('name')
    languages_ = Languages.objects.all().order_by('name')
    security_guards = SecurityGuard.objects.filter(
        is_approved=True,
        availability=True,
    ).prefetch_related('languages')
    base_itinerary = ItineraryItem.objects.filter(tour=find_tour)
    user_itinerary_items = UserItineraryItem.objects.filter(user=user, tour=find_tour)
    customized_by_base_id = {
        item.itinerary_item_id: item for item in user_itinerary_items
    }
    final_itinerary = [
        customized_by_base_id.get(item.id, item) for item in base_itinerary
    ]

    initial_date = find_tour.start_date or timezone.localdate()
    form = BookingForm(
        request.POST or None,
        initial={
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'booking_date': initial_date,
            'adults': 1,
            'children': 0,
        },
    )
    selected_language_codes = (
        request.POST.getlist('languages') or request.POST.getlist('language[]')
        if request.method == 'POST' else []
    )

    if request.method == 'POST' and form.is_valid():
        selected_languages = list(Languages.objects.filter(code__in=selected_language_codes))
        selected_accommodation = None
        selected_security_guard = None

        accommodation_id = request.POST.get('selected_accommodations')
        if accommodation_id:
            selected_accommodation = get_object_or_404(Accommodation, id=accommodation_id)

        wants_security = request.POST.get('security') == 'on'
        if wants_security:
            matching_guards = security_guards
            if selected_languages:
                matching_guards = matching_guards.filter(
                    languages__in=selected_languages
                ).distinct()
            selected_security_guard = matching_guards.first()
            if selected_security_guard is None:
                form.add_error(None, 'No approved security guard is currently available for this request.')

        if form.is_valid():
            adults = form.cleaned_data['adults']
            children = form.cleaned_data['children']
            travellers = adults + children
            base_total = Decimal(find_tour.price) * travellers
            accommodation_total = Decimal('0')
            language_total = sum(
                (Decimal(str(language.total_price)) for language in selected_languages),
                Decimal('0'),
            )
            security_total = Decimal('0')

            if selected_accommodation:
                accommodation_total = Decimal(str(selected_accommodation.total_price or 0))
            if selected_security_guard:
                security_total = Decimal(str(selected_security_guard.total_price or 0))

            total_price = base_total + accommodation_total + language_total + security_total
            service_lines = [
                f'Tour base: {travellers} traveller(s) × ${find_tour.price}',
            ]
            if selected_accommodation:
                service_lines.append(f'Accommodation: {selected_accommodation.name} (${accommodation_total})')
            if selected_languages:
                service_lines.append(
                    'Translation languages: ' + ', '.join(language.name for language in selected_languages)
                )
            if selected_security_guard:
                service_lines.append(f'Security guard: {selected_security_guard.name} (${security_total})')
            service_lines.append(f'Quoted total: ${total_price}')

            customer_notes = form.cleaned_data.get('notes', '').strip()
            booking_notes = customer_notes
            if booking_notes:
                booking_notes += '\n\n'
            booking_notes += '--- Selected services ---\n' + '\n'.join(service_lines)

            with transaction.atomic():
                booking = form.save(commit=False)
                booking.user = user
                booking.tour = find_tour
                booking.situation = 'Booked'
                booking.paid = False
                booking.paid_amount = int(total_price.quantize(
                    Decimal('1'), rounding=ROUND_HALF_UP
                ))
                booking.notes = booking_notes
                booking.save()

                if selected_accommodation:
                    for item in base_itinerary:
                        customized_item = UserItineraryItem.objects.filter(
                            user=user,
                            itinerary_item=item,
                        ).first()
                        if customized_item:
                            customized_item.accommodation = selected_accommodation
                            customized_item.save(update_fields=['accommodation'])
                        else:
                            UserItineraryItem.objects.create(
                                user=user,
                                itinerary_item=item,
                                accommodation=selected_accommodation,
                                transport=item.transport,
                                title=item.title,
                                description=item.description,
                                image=item.image,
                                date=item.date,
                                day_number=item.day_number,
                                type_of_transport=item.type_of_transport,
                                tour_guide=item.tour_guide,
                                meals=item.meals,
                                logistics=item.logistics,
                                tour=item.tour,
                            )

            messages.success(request, 'Your booking was created. Complete payment to confirm your trip.')
            return redirect('tour:payment', booking_id=booking.id)

    context = {
        'get_tour_categories': TourCategory.objects.all(),
        'find_tour': find_tour,
        'get_interary': final_itinerary,
        'selected_language_codes': selected_language_codes,
        'languages_': languages_,
        'security_guards': security_guards,
        'accommodation': accommodation,
        'form': form,
    }
    return render(request, 'tour/tour-booking.html', context)



@login_required
def edit_itinerary(request, itienary_id, user_id):
    if request.user.id != user_id and not request.user.is_staff:
        raise PermissionDenied
    try:
        user_itinerary = UserItineraryItem.objects.get(id=itienary_id, user=user_id)
        base_itinerary = user_itinerary.itinerary_item  # always keep the base itinerary
    except UserItineraryItem.DoesNotExist:
        # Otherwise just load the base itinerary
        base_itinerary = ItineraryItem.objects.get(id=itienary_id)
        user_itinerary = None
    user = get_object_or_404(User, id=user_id)

    accommodation = Accommodation.objects.all()
    transport = Transport.objects.all()

    # Just get one directly from the object
    selected_transport = (
        user_itinerary.transport if user_itinerary and user_itinerary.transport else base_itinerary.transport
    )
    selected_accommodation = (
        user_itinerary.accommodation if user_itinerary and user_itinerary.accommodation else base_itinerary.accommodation
    )

    if request.method == 'POST':
        accommodation_id = request.POST.get('selected_accommodations')   
        transport_id = request.POST.get('selected_transport')
        if accommodation_id:
            selected_accommodation = get_object_or_404(Accommodation, id=accommodation_id)
        if transport_id:
            selected_transport = get_object_or_404(Transport, id=transport_id)

        # Save or update the user’s itinerary
        user_itinerary, created = UserItineraryItem.objects.update_or_create(
            user=user,
            itinerary_item=base_itinerary,  # ✅ always the base itinerary here
            defaults={
                'accommodation': selected_accommodation,
                'transport': selected_transport,
                'title': base_itinerary.title,
                'description': base_itinerary.description,
                'image': base_itinerary.image,
                'date': base_itinerary.date,
                'day_number': base_itinerary.day_number,
                'type_of_transport': base_itinerary.type_of_transport,
                'tour_guide': base_itinerary.tour_guide,
                'meals': base_itinerary.meals,
                'logistics': base_itinerary.logistics,
                'tour': base_itinerary.tour,
            }
        )
        return redirect('tour:tour_booking', base_itinerary.tour.slug)
        # Optionally redirect or return an HTMX response

    context = {
        'get_itienary': user_itinerary or base_itinerary,
        'selected_transport':selected_transport,
        'selected_accommodation':selected_accommodation,
        'accommodation':accommodation,
        'transport':transport,
    }
    return render(request, 'tour/customize-tour.html', context) 


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






def _customer_booking_queryset(user):
    return Booking.objects.filter(user=user, tour__isnull=False).select_related(
        'tour',
        'tour__tour_guide',
        'tour__translator',
        'tour__security_gard',
    ).prefetch_related('tour__crew_engagements__crew', 'tour__crew_engagements__role')


@login_required
def dashboard_router(request):
    if (
        request.user.is_staff
        or request.user.is_superuser
        or request.user.my_choice_field in {'Operator', 'Moderator'}
    ):
        return redirect('tour:operations:dashboard')

    if hasattr(request.user, 'crew_profile'):
        return redirect('tour:crew:dashboard')
    if hasattr(request.user, 'supplier_profile'):
        return redirect('tour:supplier:dashboard')

    user_type = request.user.my_choice_field or 'Tourist'
    if user_type == 'Tourist':
        return redirect('tour:customer_dashboard')
    return redirect('tour:user_newsfeed')


@login_required
def customer_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('tour:tg_doc_dashboard')
    if (request.user.my_choice_field or 'Tourist') != 'Tourist':
        return redirect('tour:user_newsfeed')

    bookings = _customer_booking_queryset(request.user)
    total_paid = bookings.filter(paid=True).aggregate(
        total=Sum('paid_amount')
    )['total'] or 0
    pending_payment = bookings.filter(paid=False).exclude(situation='Cancelled')
    upcoming = bookings.filter(situation='upcoming')
    in_progress = bookings.filter(situation='in_progress')
    completed = bookings.filter(situation__in=['completed', 'Reviewed'])
    cancelled = bookings.filter(situation='Cancelled')
    next_booking = upcoming.order_by('tour__start_date', 'booking_date').first()
    if next_booking is None:
        next_booking = pending_payment.order_by('tour__start_date', 'booking_date').first()

    action_items = []
    payment_booking = pending_payment.order_by('booking_date').first()
    if payment_booking:
        action_items.append({
            'title': 'Complete payment',
            'description': f'Confirm {payment_booking.tour.title} by completing payment.',
            'url': reverse('tour:payment', args=[payment_booking.id]),
            'icon': 'ti-credit-card',
        })

    if next_booking and next_booking.paid:
        has_pre_arrival = (
            PreArrivalRequirement.objects.filter(booking=next_booking).exists()
            or PreArrival.objects.filter(booking=next_booking).exists()
        )
        if not has_pre_arrival:
            action_items.append({
                'title': 'Complete pre-arrival information',
                'description': 'Add passport, visa, arrival, and emergency contact details.',
                'url': reverse('tour:up_commoing_tours_more_info', args=[next_booking.id]),
                'icon': 'ti-file-description',
            })

    context = {
        'total_bookings': bookings.count(),
        'pending_count': pending_payment.count(),
        'upcoming_count': upcoming.count(),
        'in_progress_count': in_progress.count(),
        'completed_count': completed.count(),
        'cancelled_count': cancelled.count(),
        'total_paid': total_paid,
        'next_booking': next_booking,
        'recent_bookings': bookings.order_by('-id')[:5],
        'wishlist_count': User_favorite_tour.objects.filter(
            user=request.user,
            favorite=True,
        ).count(),
        'action_items': action_items,
    }
    return render(request, 'tour/tourist_newsfeed.html', context)


@login_required
def tg_doc_dashboard(request):
    user = request.user
    if user.is_staff or user.is_superuser or user.my_choice_field in {'Operator', 'Moderator'}:
        return redirect('tour:operations:dashboard')
    if (user.my_choice_field or 'Tourist') == 'Tourist' and not user.is_staff:
        return redirect('tour:customer_dashboard')
    context = {
        'username': user.username,
        'email': user.email,
        'last_login': user.last_login,
        'date_joined': user.date_joined,
    }
    return render(request, 'tour_involve/tg_dashboard.html', context)



@login_required
def user_newsfeed(request):
    user = request.user
    user_type = user.my_choice_field or 'Tourist'

    all_tours_assignment = TourGuideAssignment.objects.filter(status=True)

    context = {
        'all_tours_assignment': all_tours_assignment,
    }

    # Conditionally render different templates based on user type
    if user_type == 'Tourist':
        return redirect('tour:customer_dashboard')
    elif user_type == 'Guide':
        return render(request, 'tour_involve/tg_doc_newsfeed.html', context)
    else:
        return render(request, 'tour_involve/tg_doc_newsfeed.html', context)
    


@login_required
def payment(request, booking_id=None):
    bookings = _customer_booking_queryset(request.user)
    if booking_id is None:
        booking = bookings.filter(paid=False).order_by('-id').first()
        if booking is None:
            messages.info(request, 'You have no outstanding payments.')
            return redirect('tour:customer_dashboard')
        return redirect('tour:payment', booking_id=booking.id)

    booking = get_object_or_404(bookings, id=booking_id)
    return render(request, 'tour/payment.html', {
        'booking': booking,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


def _mark_booking_paid(booking, amount_total=None):
    if amount_total is not None:
        booking.paid_amount = int(Decimal(amount_total) / Decimal('100'))
    booking.paid = True
    if booking.situation == 'Booked':
        booking.situation = 'upcoming'
    booking.save(update_fields=['paid', 'paid_amount', 'situation'])


@login_required
@require_POST
def create_checkout_session(request, booking_id):
    booking = get_object_or_404(
        _customer_booking_queryset(request.user),
        id=booking_id,
    )
    if booking.paid:
        messages.info(request, 'This booking is already paid.')
        return redirect('tour:customer_dashboard')
    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Payment is not configured yet. Please contact support.')
        return redirect('tour:payment', booking_id=booking.id)


    amount = max(int(Decimal(booking.paid_amount or 0) * 100), 50)
    success_url = request.build_absolute_uri(
        reverse('tour:payment_success', args=[booking.id])
    ) + '?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.build_absolute_uri(
        reverse('tour:payment_cancel', args=[booking.id])
    )

    try:
        checkout_session = stripe.checkout.Session.create(
            mode='payment',
            client_reference_id=str(booking.id),
            customer_email=booking.email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': booking.tour.title,
                        'description': f'AfghanAwaits tour booking #{booking.id}',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            metadata={
                'booking_id': str(booking.id),
                'user_id': str(request.user.id),
            },
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except stripe.error.StripeError:
        messages.error(request, 'Payment service is temporarily unavailable. Please try again.')
        return redirect('tour:payment', booking_id=booking.id)

    return redirect(checkout_session.url, permanent=False)


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(
        _customer_booking_queryset(request.user),
        id=booking_id,
    )
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, 'Payment confirmation is missing.')
        return redirect('tour:payment', booking_id=booking.id)

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        messages.error(request, 'We could not verify this payment yet.')
        return redirect('tour:payment', booking_id=booking.id)

    metadata = checkout_session.get('metadata') or {}
    if (
        checkout_session.get('payment_status') != 'paid'
        or str(metadata.get('booking_id')) != str(booking.id)
        or str(metadata.get('user_id')) != str(request.user.id)
    ):
        messages.error(request, 'Payment has not been confirmed.')
        return redirect('tour:payment', booking_id=booking.id)

    _mark_booking_paid(booking, checkout_session.get('amount_total'))
    messages.success(request, 'Payment confirmed. Your trip is now in Upcoming Tours.')
    return redirect('tour:customer_dashboard')


@login_required
def payment_cancel(request, booking_id):
    booking = get_object_or_404(
        _customer_booking_queryset(request.user),
        id=booking_id,
    )
    messages.warning(request, 'Payment was cancelled. Your booking is saved and can be paid later.')
    return redirect('tour:payment', booking_id=booking.id)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return HttpResponse(status=503)
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get('HTTP_STRIPE_SIGNATURE', ''),
            webhook_secret,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        booking_id = (checkout_session.get('metadata') or {}).get('booking_id')
        booking = Booking.objects.filter(id=booking_id).first()
        if booking and checkout_session.get('payment_status') == 'paid':
            _mark_booking_paid(booking, checkout_session.get('amount_total'))
    return HttpResponse(status=200)




@login_required
def up_commoing_tours(request):
    return redirect(reverse('tour:customer_tours') + '?status=upcoming')


@login_required
def customer_tours(request):
    bookings = _customer_booking_queryset(request.user)
    status = request.GET.get('status', 'all')
    search = request.GET.get('q', '').strip()
    status_filters = {
        'pending': Q(paid=False) & ~Q(situation='Cancelled'),
        'upcoming': Q(situation='upcoming'),
        'in_progress': Q(situation='in_progress'),
        'completed': Q(situation__in=['completed', 'Reviewed']),
        'cancelled': Q(situation='Cancelled'),
    }
    if status in status_filters:
        bookings = bookings.filter(status_filters[status])
    else:
        status = 'all'
    if search:
        bookings = bookings.filter(
            Q(tour__title__icontains=search)
            | Q(tour__location__icontains=search)
        )

    paginator = Paginator(bookings.order_by('-booking_date', '-id'), 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tour/upcomming_tours/tourist_upcomming_tour.html', {
        'upcomming_tours': page_obj.object_list,
        'page_obj': page_obj,
        'selected_status': status,
        'search_query': search,
        'all_count': _customer_booking_queryset(request.user).count(),
    })
    
    




@login_required
def up_commoing_tours_more_info(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    edit_mode = request.GET.get('edit') == '1'
    if not booking.paid:
        messages.warning(request, 'Complete payment before managing pre-arrival information.')
        return redirect('tour:payment', booking_id=booking.id)

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
    if not booking.paid:
        messages.warning(request, 'Complete payment before submitting pre-arrival information.')
        return redirect('tour:payment', booking_id=booking.id)



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
    if not request.user.is_staff:
        raise PermissionDenied


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
            return redirect('tour:pickup_plan_detail', booking_id=booking.id)
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
    if request.user != booking.user and not request.user.is_staff:
        raise PermissionDenied
    if not booking.paid and not request.user.is_staff:
        messages.warning(request, 'Complete payment before viewing pickup arrangements.')
        return redirect('tour:payment', booking_id=booking.id)
    return render(request, 'tour/upcomming_tours/tourist_arrival_pickup.html', {
        'booking': booking, 'pickup': pickup, 'itinerary_items':itinerary_items,
    })


@login_required
@require_POST
def pickup_update_status(request, booking_id):
    if not request.user.is_staff:
        raise PermissionDenied
    pickup = get_object_or_404(PickupPlan, booking_id=booking_id)
    new_status = request.POST.get('status')
    if new_status not in dict(PickupPlan.STATUS):
        messages.error(request, 'Invalid pickup status.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    pickup.status = new_status
    if new_status == 'picked_up':
        pickup.mark_picked_up()
    else:
        pickup.save(update_fields=['status', 'updated_at'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))



@login_required
def welcome_package_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')


    # Restrict access so only the booking owner or staff can view
    if request.user != booking.user and not request.user.is_staff:
        raise PermissionDenied
    if not booking.paid and not request.user.is_staff:
        messages.warning(request, 'Complete payment before viewing the welcome package.')
        return redirect('tour:payment', booking_id=booking.id)

    package = getattr(booking, 'welcome_package', None)

    # For an elegant empty state
    gifts = package.gifts.all() if package else []

    return render(request, "tour/upcomming_tours/tourist_wellcom_package.html", {
        "booking": booking,
        "package": package,
        "gifts": gifts,
        'itinerary_items':itinerary_items,
    })



@login_required
def itenary_full_info(request, id, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    tour = booking.tour
    itinerary_items = tour.itinerary_items.all().order_by('day_number')

    item_id = id

    if request.user != booking.user and not request.user.is_staff:
        raise PermissionDenied
    if not booking.paid and not request.user.is_staff:
        messages.warning(request, 'Complete payment before viewing the full itinerary.')
        return redirect('tour:payment', booking_id=booking.id)
    item = get_object_or_404(
        ItineraryItem.objects.select_related(
            "tour", "accommodation", "transport", "tour_guide", "meals", "logistics"
        ),
        id=item_id,
        tour=booking.tour,
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
