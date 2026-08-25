import csv
from functools import wraps

from django.contrib import messages
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Booking,
    PickupPlan,
    PreArrival,
    PreArrivalRequirement,
    SecurityGuard,
    Tour,
    TourGuide,
    Translator,
    WelcomePackage,
)
from .operations_forms import (
    BookingOperationsForm,
    BookingStatusForm,
    ManualPaymentForm,
    PickupPlanOperationsForm,
    TourOperationsForm,
    WelcomePackageOperationsForm,
)


User = get_user_model()

OPERATIONS_ROLES = {'Operator', 'Moderator'}

BOOKING_TRANSITIONS = {
    'Booked': ('upcoming', 'Cancelled'),
    'upcoming': ('in_progress', 'Cancelled'),
    'in_progress': ('completed', 'Cancelled'),
    'completed': ('Reviewed',),
    'Reviewed': (),
    'Cancelled': ('Booked',),
}


def has_operations_access(user):
    return bool(
        user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
            or user.my_choice_field in OPERATIONS_ROLES
        )
    )


def operations_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not has_operations_access(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped


def can_record_manual_payment(user):
    return user.is_superuser or user.my_choice_field == 'Moderator'


def _booking_queryset():
    return Booking.objects.select_related(
        'tour', 'user', 'tour__tour_guide', 'tour__translator',
        'tour__security_gard',
    )


def _log_change(request, obj, message):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=content_type.pk,
        object_id=obj.pk,
        object_repr=str(obj)[:200],
        action_flag=CHANGE,
        change_message=message,
    )


def _booking_logs(booking):
    content_type = ContentType.objects.get_for_model(Booking)
    return LogEntry.objects.filter(
        content_type=content_type,
        object_id=str(booking.pk),
    ).select_related('user').order_by('-action_time')


def _apply_booking_filters(request, queryset):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    payment = request.GET.get('payment', '').strip()
    tour_id = request.GET.get('tour', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if query:
        queryset = queryset.filter(
            Q(id__icontains=query)
            | Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(user__username__icontains=query)
            | Q(tour__title__icontains=query)
        )
    if status in dict(Booking.BOOKING_SIT):
        queryset = queryset.filter(situation=status)
    if payment == 'paid':
        queryset = queryset.filter(paid=True)
    elif payment == 'unpaid':
        queryset = queryset.filter(paid=False)
    if tour_id.isdigit():
        queryset = queryset.filter(tour_id=int(tour_id))
    if date_from:
        queryset = queryset.filter(booking_date__gte=date_from)
    if date_to:
        queryset = queryset.filter(booking_date__lte=date_to)
    return queryset


@operations_required
def dashboard(request):
    today = timezone.localdate()
    next_week = today + timezone.timedelta(days=7)
    bookings = _booking_queryset()
    booking_flags = bookings.annotate(
        has_requirement=Exists(
            PreArrivalRequirement.objects.filter(booking_id=OuterRef('pk'))
        ),
        has_pre_arrival=Exists(
            PreArrival.objects.filter(booking_id=OuterRef('pk'))
        ),
        has_pickup=Exists(
            PickupPlan.objects.filter(booking_id=OuterRef('pk'))
        ),
    )

    pending_documents = booking_flags.filter(
        paid=True,
        situation__in=['upcoming', 'in_progress'],
        has_requirement=False,
        has_pre_arrival=False,
    )
    pickup_attention = booking_flags.filter(
        paid=True,
        situation='upcoming',
        tour__start_date__range=(today, next_week),
        has_pickup=False,
    )
    departures = Tour.objects.filter(
        start_date__gte=today,
    ).annotate(
        booking_count=Count('bookings'),
        paid_count=Count('bookings', filter=Q(bookings__paid=True)),
    ).order_by('start_date')[:8]

    context = {
        'new_requests': bookings.filter(situation='Booked', paid=False).count(),
        'awaiting_payment': bookings.filter(paid=False).exclude(situation='Cancelled').count(),
        'confirmed_count': bookings.filter(paid=True, situation='upcoming').count(),
        'in_progress_count': bookings.filter(situation='in_progress').count(),
        'completed_count': bookings.filter(situation__in=['completed', 'Reviewed']).count(),
        'pending_documents_count': pending_documents.count(),
        'pickup_attention_count': pickup_attention.count(),
        'revenue_total': bookings.filter(paid=True).aggregate(total=Sum('paid_amount'))['total'] or 0,
        'latest_bookings': bookings.order_by('-id')[:8],
        'departures': departures,
        'attention_bookings': pending_documents.order_by('tour__start_date')[:5],
        'pickup_attention': pickup_attention.order_by('tour__start_date')[:5],
        'today': today,
    }
    return render(request, 'operations/dashboard.html', context)


@operations_required
def booking_list(request):
    bookings = _apply_booking_filters(request, _booking_queryset()).order_by('-id')
    page_obj = Paginator(bookings, 25).get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
        'bookings': page_obj.object_list,
        'tours': Tour.objects.order_by('-start_date', 'title'),
        'status_choices': Booking.BOOKING_SIT,
        'query': request.GET.get('q', ''),
        'selected_status': request.GET.get('status', ''),
        'selected_payment': request.GET.get('payment', ''),
        'selected_tour': request.GET.get('tour', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
    }
    return render(request, 'operations/bookings/list.html', context)


@operations_required
def booking_export(request):
    bookings = _apply_booking_filters(request, _booking_queryset()).order_by('-id')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Booking ID', 'Tour', 'Customer', 'Email', 'Phone', 'Travel date',
        'Adults', 'Children', 'Status', 'Paid', 'Amount',
    ])
    for booking in bookings:
        writer.writerow([
            booking.id,
            booking.tour.title if booking.tour else '',
            booking.name,
            booking.email,
            booking.phone,
            booking.booking_date,
            booking.adults,
            booking.children,
            booking.situation,
            'Yes' if booking.paid else 'No',
            booking.paid_amount or 0,
        ])
    return response


@operations_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(_booking_queryset(), pk=booking_id)
    requirement = getattr(booking, 'pre_arrival_tour', None)
    pre_arrival = getattr(booking, 'pre_arrival', None)
    pickup = getattr(booking, 'pickup', None)
    package = getattr(booking, 'welcome_package', None)
    allowed_statuses = BOOKING_TRANSITIONS.get(booking.situation, ())

    context = {
        'booking': booking,
        'requirement': requirement,
        'pre_arrival': pre_arrival,
        'pickup': pickup,
        'package': package,
        'logs': _booking_logs(booking)[:30],
        'status_form': BookingStatusForm(allowed_statuses=allowed_statuses),
        'details_form': BookingOperationsForm(instance=booking),
        'payment_form': ManualPaymentForm(initial={'amount': booking.paid_amount or 0}),
        'can_record_payment': can_record_manual_payment(request.user),
        'allowed_statuses': allowed_statuses,
    }
    return render(request, 'operations/bookings/detail.html', context)


@operations_required
@require_POST
def booking_update_details(request, booking_id):
    booking = get_object_or_404(_booking_queryset(), pk=booking_id)
    form = BookingOperationsForm(request.POST, instance=booking)
    if form.is_valid():
        form.save()
        _log_change(request, booking, 'Customer and booking details updated from Operations Center.')
        messages.success(request, 'Booking details were updated.')
    else:
        messages.error(request, 'Please correct the booking details and try again.')
    return redirect('tour:operations:booking_detail', booking_id=booking.pk)


@operations_required
@require_POST
def booking_update_status(request, booking_id):
    booking = get_object_or_404(_booking_queryset(), pk=booking_id)
    allowed_statuses = BOOKING_TRANSITIONS.get(booking.situation, ())
    form = BookingStatusForm(request.POST, allowed_statuses=allowed_statuses)
    if not form.is_valid():
        messages.error(request, 'The requested status change is not valid.')
        return redirect('tour:operations:booking_detail', booking_id=booking.pk)

    new_status = form.cleaned_data['situation']
    if new_status not in allowed_statuses:
        raise PermissionDenied
    if new_status in {'upcoming', 'in_progress', 'completed', 'Reviewed'} and not booking.paid:
        messages.error(request, 'An unpaid booking cannot move into an operational stage.')
        return redirect('tour:operations:booking_detail', booking_id=booking.pk)
    if booking.situation == 'Cancelled' and not request.user.is_superuser:
        messages.error(request, 'Only a system administrator can reopen a cancelled booking.')
        return redirect('tour:operations:booking_detail', booking_id=booking.pk)

    previous_status = booking.situation
    booking.situation = new_status
    reason = form.cleaned_data.get('reason', '').strip()
    if reason:
        booking.notes = (booking.notes + '\n\n' if booking.notes else '') + (
            f'Operations status note: {reason}'
        )
    booking.save(update_fields=['situation', 'notes'])
    _log_change(
        request,
        booking,
        f'Status changed from {previous_status} to {new_status}. Reason: {reason or "Not provided"}',
    )
    messages.success(request, f'Booking moved to {booking.get_situation_display()}.')
    return redirect('tour:operations:booking_detail', booking_id=booking.pk)


@operations_required
@require_POST
def booking_record_payment(request, booking_id):
    if not can_record_manual_payment(request.user):
        raise PermissionDenied
    booking = get_object_or_404(_booking_queryset(), pk=booking_id)
    form = ManualPaymentForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'A valid amount, reference, and reason are required.')
        return redirect('tour:operations:booking_detail', booking_id=booking.pk)

    with transaction.atomic():
        booking.paid = True
        booking.paid_amount = form.cleaned_data['amount']
        if booking.situation == 'Booked':
            booking.situation = 'upcoming'
        payment_note = (
            f'Manual payment reference: {form.cleaned_data["reference"]}\n'
            f'Reason: {form.cleaned_data["reason"]}'
        )
        booking.notes = (booking.notes + '\n\n' if booking.notes else '') + payment_note
        booking.save(update_fields=['paid', 'paid_amount', 'situation', 'notes'])
        _log_change(
            request,
            booking,
            f'Manual payment recorded. Amount USD {booking.paid_amount}. '
            f'Reference: {form.cleaned_data["reference"]}.',
        )
    messages.success(request, 'Manual payment was recorded and audited.')
    return redirect('tour:operations:booking_detail', booking_id=booking.pk)


@operations_required
def booking_pickup(request, booking_id):
    booking = get_object_or_404(_booking_queryset(), pk=booking_id)
    pickup = getattr(booking, 'pickup', None)
    if request.method == 'POST':
        form = PickupPlanOperationsForm(request.POST, request.FILES, instance=pickup)
        if form.is_valid():
            old_status = pickup.status if pickup else None
            obj = form.save(commit=False)
            obj.booking = booking
            if obj.status == 'picked_up' and old_status != 'picked_up':
                obj.picked_up_at = timezone.now()
            obj.save()
            _log_change(
                request,
                booking,
                f'Pickup plan updated. Status: {obj.get_status_display()}.',
            )
            messages.success(request, 'Pickup plan was saved.')
            return redirect('tour:operations:booking_detail', booking_id=booking.pk)
    else:
        initial = {'tourist_phone_share': booking.phone}
        if pickup is None:
            pre_arrival = getattr(booking, 'pre_arrival', None)
            if pre_arrival:
                initial.update({
                    'entry_point_code': pre_arrival.entry_point,
                    'entry_point_label': pre_arrival.get_entry_point_display(),
                })
        form = PickupPlanOperationsForm(instance=pickup, initial=initial)
    return render(request, 'operations/bookings/pickup_form.html', {
        'booking': booking,
        'pickup': pickup,
        'form': form,
    })


@operations_required
def booking_welcome_package(request, booking_id):
    booking = get_object_or_404(_booking_queryset(), pk=booking_id)
    package = getattr(booking, 'welcome_package', None)
    if request.method == 'POST':
        form = WelcomePackageOperationsForm(
            request.POST,
            request.FILES,
            instance=package,
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.booking = booking
            obj.user = booking.user
            obj.save()
            form.save_m2m()
            _log_change(request, booking, 'Welcome package updated.')
            messages.success(request, 'Welcome package was saved.')
            return redirect('tour:operations:booking_detail', booking_id=booking.pk)
    else:
        form = WelcomePackageOperationsForm(instance=package)
    return render(request, 'operations/bookings/welcome_form.html', {
        'booking': booking,
        'package': package,
        'form': form,
    })


@operations_required
def tour_list(request):
    tours = Tour.objects.annotate(
        booking_count=Count('bookings'),
        paid_count=Count('bookings', filter=Q(bookings__paid=True)),
        active_count=Count(
            'bookings',
            filter=Q(bookings__situation__in=['upcoming', 'in_progress']),
        ),
    ).order_by('-start_date', 'title')
    query = request.GET.get('q', '').strip()
    availability = request.GET.get('availability', '')
    if query:
        tours = tours.filter(Q(title__icontains=query) | Q(location__icontains=query))
    if availability == 'available':
        tours = tours.filter(available=True)
    elif availability == 'closed':
        tours = tours.filter(available=False)
    page_obj = Paginator(tours, 20).get_page(request.GET.get('page'))
    return render(request, 'operations/tours/list.html', {
        'tours': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'availability': availability,
    })


@operations_required
def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    bookings = _booking_queryset().filter(tour=tour).order_by('booking_date', 'id')
    if request.method == 'POST':
        form = TourOperationsForm(request.POST, instance=tour)
        if form.is_valid():
            form.save()
            _log_change(request, tour, 'Tour schedule and operational assignments updated.')
            messages.success(request, 'Tour operations were updated.')
            return redirect('tour:operations:tour_detail', tour_id=tour.pk)
    else:
        form = TourOperationsForm(instance=tour)
    return render(request, 'operations/tours/detail.html', {
        'tour': tour,
        'bookings': bookings,
        'form': form,
        'traveller_count': sum((b.adults + b.children) for b in bookings),
        'paid_count': bookings.filter(paid=True).count(),
        'active_count': bookings.filter(situation__in=['upcoming', 'in_progress']).count(),
    })


@operations_required
def customer_list(request):
    customers = User.objects.filter(
        Q(my_choice_field='Tourist') | Q(my_choice_field__isnull=True)
    ).annotate(
        booking_count=Count('booked_tours'),
        total_paid=Sum('booked_tours__paid_amount', filter=Q(booked_tours__paid=True)),
    ).order_by('-date_joined')
    query = request.GET.get('q', '').strip()
    if query:
        customers = customers.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
    page_obj = Paginator(customers, 25).get_page(request.GET.get('page'))
    return render(request, 'operations/customers/list.html', {
        'customers': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
    })


@operations_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(User, pk=customer_id)
    bookings = _booking_queryset().filter(user=customer).order_by('-id')
    return render(request, 'operations/customers/detail.html', {
        'customer_record': customer,
        'bookings': bookings,
        'total_paid': bookings.filter(paid=True).aggregate(total=Sum('paid_amount'))['total'] or 0,
        'active_count': bookings.filter(situation__in=['upcoming', 'in_progress']).count(),
    })


@operations_required
def document_queue(request):
    bookings = _booking_queryset().filter(paid=True).annotate(
        has_requirement=Exists(
            PreArrivalRequirement.objects.filter(booking_id=OuterRef('pk'))
        ),
        has_pre_arrival=Exists(
            PreArrival.objects.filter(booking_id=OuterRef('pk'))
        ),
    ).order_by('tour__start_date', 'booking_date')
    state = request.GET.get('state', 'all')
    if state == 'missing':
        bookings = bookings.filter(has_requirement=False, has_pre_arrival=False)
    elif state == 'submitted':
        bookings = bookings.filter(Q(has_requirement=True) | Q(has_pre_arrival=True))
    return render(request, 'operations/documents/list.html', {
        'bookings': bookings,
        'state': state,
    })


@operations_required
def pickup_queue(request):
    plans = PickupPlan.objects.select_related(
        'booking', 'booking__tour', 'booking__user', 'driver', 'operator', 'vehicle',
    ).order_by('scheduled_at')
    status = request.GET.get('status', '')
    if status in dict(PickupPlan.STATUS):
        plans = plans.filter(status=status)
    return render(request, 'operations/pickups/list.html', {
        'plans': plans,
        'status_choices': PickupPlan.STATUS,
        'selected_status': status,
    })


@operations_required
def provider_list(request):
    return render(request, 'operations/providers/list.html', {
        'guides': TourGuide.objects.order_by('-is_approved', 'name'),
        'translators': Translator.objects.order_by('-is_approved', 'name'),
        'guards': SecurityGuard.objects.order_by('-is_approved', 'name'),
    })


@operations_required
def reports(request):
    bookings = Booking.objects.all()
    status_rows = list(
        bookings.values('situation').annotate(total=Count('id')).order_by('situation')
    )
    monthly_rows = list(
        bookings.annotate(month=TruncMonth('booking_date'))
        .values('month')
        .annotate(
            bookings=Count('id'),
            revenue=Sum('paid_amount', filter=Q(paid=True)),
        )
        .order_by('-month')[:12]
    )
    top_tours = Tour.objects.annotate(
        booking_count=Count('bookings'),
        revenue=Sum('bookings__paid_amount', filter=Q(bookings__paid=True)),
    ).order_by('-booking_count')[:10]
    return render(request, 'operations/reports.html', {
        'status_rows': status_rows,
        'monthly_rows': monthly_rows,
        'top_tours': top_tours,
        'total_revenue': bookings.filter(paid=True).aggregate(total=Sum('paid_amount'))['total'] or 0,
        'total_bookings': bookings.count(),
    })

