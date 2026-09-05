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
from django.db.models import Count, Exists, Max, OuterRef, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from home.models import EntryPlan, RouteProposal, TripRequest

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
    TripRequestOperationsForm,
    EntryPlanOperationsForm,
    RouteProposalOperationsForm,
    RouteProposalDayFormSet,
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


def _trip_request_queryset():
    return TripRequest.objects.prefetch_related(
        'stops__destination',
        'proposals__days__destination',
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

    route_status_counts = dict(
        TripRequest.objects.values_list('status').annotate(total=Count('pk'))
    )
    booking_status_counts = dict(
        bookings.values_list('situation').annotate(total=Count('pk'))
    )

    def pipeline_rows(counts, choices):
        highest = max((counts.get(value, 0) for value, _ in choices), default=0) or 1
        return [
            {
                'value': value,
                'label': label,
                'count': counts.get(value, 0),
                'percent': round((counts.get(value, 0) / highest) * 100),
            }
            for value, label in choices
        ]

    route_pipeline = pipeline_rows(
        route_status_counts,
        (
            ('submitted', 'Submitted'),
            ('under_review', 'Under review'),
            ('proposal_sent', 'Proposal sent'),
            ('changes_requested', 'Changes requested'),
            ('approved', 'Approved'),
        ),
    )
    booking_pipeline = pipeline_rows(
        booking_status_counts,
        (
            ('Booked', 'New booking'),
            ('upcoming', 'Upcoming'),
            ('in_progress', 'In progress'),
            ('completed', 'Completed'),
        ),
    )

    context = {
        'route_request_count': TripRequest.objects.filter(
            status__in=('submitted', 'under_review', 'changes_requested')
        ).count(),
        'new_requests': bookings.filter(situation='Booked', paid=False).count(),
        'awaiting_payment': bookings.filter(paid=False).exclude(situation='Cancelled').count(),
        'confirmed_count': bookings.filter(paid=True, situation='upcoming').count(),
        'in_progress_count': bookings.filter(situation='in_progress').count(),
        'completed_count': bookings.filter(situation__in=['completed', 'Reviewed']).count(),
        'pending_documents_count': pending_documents.count(),
        'pickup_attention_count': pickup_attention.count(),
        'revenue_total': bookings.filter(paid=True).aggregate(total=Sum('paid_amount'))['total'] or 0,
        'latest_bookings': bookings.order_by('-id')[:8],
        'latest_route_requests': _trip_request_queryset().order_by('-submitted_at')[:6],
        'departures': departures,
        'attention_bookings': pending_documents.order_by('tour__start_date')[:5],
        'pickup_attention': pickup_attention.order_by('tour__start_date')[:5],
        'route_pipeline': route_pipeline,
        'booking_pipeline': booking_pipeline,
        'recent_activity': LogEntry.objects.select_related(
            'user', 'content_type'
        ).order_by('-action_time')[:8],
        'today': today,
    }
    return render(request, 'operations/dashboard.html', context)


@operations_required
def trip_request_list(request):
    queryset = _trip_request_queryset()
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    entry_status = request.GET.get('entry_status', '').strip()
    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(country_of_origin__icontains=query)
            | Q(stops__destination__title__icontains=query)
        ).distinct()
    if status in dict(TripRequest.STATUS_CHOICES):
        queryset = queryset.filter(status=status)
    if entry_status in dict(EntryPlan.STATUS_CHOICES):
        queryset = queryset.filter(entry_plan__status=entry_status)
    page_obj = Paginator(queryset.order_by('-submitted_at'), 20).get_page(request.GET.get('page'))
    return render(request, 'operations/trips/list.html', {
        'trip_requests': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'selected_status': status,
        'selected_entry_status': entry_status,
        'status_choices': TripRequest.STATUS_CHOICES,
        'entry_status_choices': EntryPlan.STATUS_CHOICES,
    })


@operations_required
def trip_request_detail(request, trip_id):
    trip_request = get_object_or_404(_trip_request_queryset(), pk=trip_id)
    entry_plan, _ = EntryPlan.objects.get_or_create(
        trip_request=trip_request,
        defaults={'arrival_origin': trip_request.country_of_origin},
    )
    return render(request, 'operations/trips/detail.html', {
        'trip_request': trip_request,
        'entry_plan': entry_plan,
        'trip_form': TripRequestOperationsForm(instance=trip_request, prefix='trip'),
        'entry_form': EntryPlanOperationsForm(instance=entry_plan, prefix='entry'),
        'proposals': trip_request.proposals.prefetch_related('days__destination'),
        'accepted_proposal': trip_request.proposals.filter(status='accepted').first(),
    })


@operations_required
@require_POST
def trip_request_update(request, trip_id):
    trip_request = get_object_or_404(TripRequest, pk=trip_id)
    entry_plan, _ = EntryPlan.objects.get_or_create(
        trip_request=trip_request,
        defaults={'arrival_origin': trip_request.country_of_origin},
    )
    trip_form = TripRequestOperationsForm(request.POST, instance=trip_request, prefix='trip')
    entry_form = EntryPlanOperationsForm(request.POST, instance=entry_plan, prefix='entry')
    if trip_form.is_valid() and entry_form.is_valid():
        with transaction.atomic():
            trip_request = trip_form.save()
            entry_plan = entry_form.save(commit=False)
            if entry_plan.status == 'confirmed':
                entry_plan.confirmed_by_id = request.user.pk
                entry_plan.confirmed_at = timezone.now()
            entry_plan.save()
            _log_change(
                request,
                trip_request,
                f'Route request updated. Status: {trip_request.get_status_display()}. '
                f'Entry plan: {entry_plan.get_status_display()}.',
            )
        messages.success(request, 'Route request and entry recommendation were updated.')
    else:
        messages.error(request, 'Please correct the route request or entry plan fields.')
    return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)


def _proposal_day_initial(trip_request):
    initial = []
    day_number = 1
    for stop in trip_request.stops.all():
        for _ in range(max(stop.nights, 1)):
            initial.append({
                'day_number': day_number,
                'destination': stop.destination,
                'title': f'{stop.destination.title} · day {day_number}',
                'description': stop.notes or f'Activities and local coordination in {stop.destination.title}.',
                'overnight_location': stop.destination.title,
            })
            day_number += 1
    return initial or [{'day_number': 1, 'title': 'Arrival and orientation'}]


@operations_required
def trip_proposal_form(request, trip_id, proposal_id=None):
    trip_request = get_object_or_404(_trip_request_queryset(), pk=trip_id)
    if proposal_id:
        proposal = get_object_or_404(RouteProposal, pk=proposal_id, trip_request=trip_request)
        if proposal.status != 'draft':
            messages.error(request, 'Sent or accepted proposals are locked. Create a new version instead.')
            return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)
    else:
        next_version = (
            trip_request.proposals.aggregate(max_version=Max('version'))['max_version'] or 0
        ) + 1
        entry_plan = getattr(trip_request, 'entry_plan', None)
        entry_label = ''
        if entry_plan:
            entry_label = (
                entry_plan.recommended_entry_point
                or entry_plan.selected_entry_point_label
            )
        proposal = RouteProposal(
            trip_request=trip_request,
            version=next_version,
            title=f'Custom Afghanistan route · {trip_request.reference}',
            proposed_entry_point=entry_label,
            total_price=trip_request.estimated_budget or 0,
            created_by_id=request.user.pk,
        )

    if request.method == 'POST':
        form = RouteProposalOperationsForm(request.POST, instance=proposal)
        day_formset = RouteProposalDayFormSet(request.POST, instance=proposal, prefix='days')
        if form.is_valid() and day_formset.is_valid():
            with transaction.atomic():
                proposal = form.save(commit=False)
                proposal.trip_request = trip_request
                proposal.created_by_id = proposal.created_by_id or request.user.pk
                proposal.status = 'draft'
                proposal.save()
                day_formset.instance = proposal
                day_formset.save()
                if trip_request.status in {'submitted', 'changes_requested'}:
                    trip_request.status = 'under_review'
                    trip_request.save(update_fields=('status', 'updated_at'))
                _log_change(request, trip_request, f'Route proposal v{proposal.version} saved as draft.')
            messages.success(request, f'Proposal v{proposal.version} was saved as a draft.')
            return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)
    else:
        form = RouteProposalOperationsForm(instance=proposal)
        day_formset = RouteProposalDayFormSet(
            instance=proposal,
            prefix='days',
            initial=_proposal_day_initial(trip_request) if proposal.pk is None else None,
        )
    return render(request, 'operations/trips/proposal_form.html', {
        'trip_request': trip_request,
        'proposal': proposal,
        'form': form,
        'day_formset': day_formset,
    })


@operations_required
@require_POST
def trip_proposal_send(request, trip_id, proposal_id):
    trip_request = get_object_or_404(TripRequest, pk=trip_id)
    proposal = get_object_or_404(
        RouteProposal.objects.prefetch_related('days'),
        pk=proposal_id,
        trip_request=trip_request,
        status='draft',
    )
    if not proposal.days.exists():
        messages.error(request, 'Add at least one itinerary day before sending the proposal.')
        return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)
    with transaction.atomic():
        proposal.status = 'sent'
        proposal.sent_at = timezone.now()
        proposal.save(update_fields=('status', 'sent_at', 'updated_at'))
        trip_request.status = 'proposal_sent'
        trip_request.save(update_fields=('status', 'updated_at'))
        entry_plan = getattr(trip_request, 'entry_plan', None)
        if entry_plan and proposal.proposed_entry_point:
            entry_plan.recommended_entry_point = proposal.proposed_entry_point
            if entry_plan.status == 'pending':
                entry_plan.status = 'recommended'
            entry_plan.save(update_fields=('recommended_entry_point', 'status'))
        _log_change(request, trip_request, f'Route proposal v{proposal.version} sent to traveller.')
    messages.success(request, f'Proposal v{proposal.version} is now visible to the traveller.')
    return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)


@operations_required
@require_POST
def trip_request_convert_booking(request, trip_id):
    trip_request = get_object_or_404(TripRequest, pk=trip_id)
    if trip_request.booking_id:
        messages.info(request, 'This route request already has a booking.')
        return redirect('tour:operations:booking_detail', booking_id=trip_request.booking_id)
    proposal = trip_request.proposals.filter(status='accepted').first()
    if proposal is None:
        messages.error(request, 'The traveller must accept a proposal before a booking can be created.')
        return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)
    tour = proposal.booking_tour
    if tour is None:
        messages.error(request, 'Link a published, bookable tour to the accepted proposal before conversion.')
        return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)
    customer = User.objects.filter(pk=trip_request.user_id).first()
    if customer is None:
        customer = User.objects.filter(email__iexact=trip_request.email).first()
    if customer is None:
        messages.error(
            request,
            'The traveller needs a registered account before this proposal can become a booking.',
        )
        return redirect('tour:operations:trip_request_detail', trip_id=trip_request.pk)
    with transaction.atomic():
        booking = Booking.objects.create(
            tour=tour,
            user=customer,
            booking_date=trip_request.start_date,
            name=trip_request.full_name,
            email=trip_request.email,
            phone=trip_request.phone,
            situation='Booked',
            adults=trip_request.adults,
            children=trip_request.children,
            paid=False,
            paid_amount=int(proposal.total_price),
            notes=(
                f'Created from custom route {trip_request.reference}.\n'
                f'Accepted proposal v{proposal.version}.\n'
                f'Entry point: {proposal.proposed_entry_point}.'
            ),
        )
        trip_request.booking_id = booking.pk
        trip_request.status = 'booked'
        trip_request.save(update_fields=('booking_id', 'status', 'updated_at'))
        _log_change(request, trip_request, f'Converted to booking #AA-{booking.pk:05d}.')
    messages.success(request, f'Booking #AA-{booking.pk:05d} was created from the accepted route.')
    return redirect('tour:operations:booking_detail', booking_id=booking.pk)


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
