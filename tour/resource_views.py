from datetime import timedelta
from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Booking, CrewApplication, CrewAvailability, CrewCase, CrewDocument,
    CrewEngagement, CrewMember, CrewNotification, CrewOffer, CrewOpportunity,
    CrewPayment, CrewQualification, CrewReview, CrewTrainingRecord,
    EmployeeProfile, RequestForQuote, ServiceOrder, ServiceRequirement,
    ServiceSupplier, SupplierAsset, SupplierContract, SupplierDocument,
    SupplierInvoice, SupplierQuote, SupplierRate, SupplierReview,
    SupplierService, Tour, TrainingCourse,
)
from .operations_views import can_record_manual_payment, operations_required
from .resource_forms import (
    CrewApplicationForm, CrewApplicationReviewForm, CrewAvailabilityForm,
    CrewCaseForm, CrewCaseResolutionForm, CrewDocumentForm,
    CrewDocumentReviewForm, CrewEngagementForm, CrewEngagementStatusForm,
    CrewOfferForm, CrewOpsProfileForm, CrewPaymentForm, CrewProfileForm,
    CrewQualificationForm, CrewReviewForm, CrewTrainingRecordForm,
    EmployeeProfileForm, RFQForm, ServiceOrderForm, ServiceOrderStatusForm,
    ServiceRequirementForm, SupplierAssetForm, SupplierContractForm,
    SupplierDocumentForm, SupplierInvoiceForm, SupplierInvoiceReviewForm,
    SupplierOpsForm, SupplierProfileForm, SupplierQuoteForm, SupplierRateForm,
    SupplierReviewForm, SupplierServiceForm, TrainingCourseForm,
)

User = get_user_model()


def _related_or_none(user, name):
    try:
        return getattr(user, name)
    except ObjectDoesNotExist:
        return None


def crew_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        request.crew = _related_or_none(request.user, 'crew_profile')
        if request.crew is None:
            return redirect('tour:crew:onboarding')
        return view_func(request, *args, **kwargs)
    return wrapped


def supplier_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        request.supplier = _related_or_none(request.user, 'supplier_profile')
        if request.supplier is None:
            return redirect('tour:supplier:onboarding')
        return view_func(request, *args, **kwargs)
    return wrapped


def _notify(crew, title, message, url=''):
    CrewNotification.objects.create(crew=crew, title=title, message=message, url=url)


def _crew_eligibility(crew, opportunity):
    reasons = []
    if not crew.is_approved:
        reasons.append('Your workforce profile is not approved yet.')
    if not crew.available_for_work:
        reasons.append('Your profile is marked unavailable for work.')
    qualification = crew.qualifications.filter(role=opportunity.role, is_active=True).first()
    if qualification is None:
        reasons.append('The required role is not listed on your profile.')
    elif not qualification.is_verified:
        reasons.append('The required role has not been verified.')
    elif qualification.experience_years < opportunity.minimum_experience_years:
        reasons.append('The minimum experience requirement is not met.')
    if crew.availability_blocks.filter(
        availability_type='unavailable', start_at__lt=opportunity.end_at,
        end_at__gt=opportunity.start_at,
    ).exists():
        reasons.append('Your availability calendar blocks this period.')
    if crew.engagements.filter(
        status__in=CrewEngagement.ACTIVE_STATUSES, start_at__lt=opportunity.end_at,
        end_at__gt=opportunity.start_at,
    ).exists():
        reasons.append('You are already booked during this period.')
    return not reasons, reasons


def _refresh_crew_score(crew):
    stats = crew.engagements.filter(status='completed').aggregate(total=Count('id'))
    reviews = CrewReview.objects.filter(engagement__crew=crew).aggregate(avg=Avg('overall'), total=Count('id'))
    crew.completed_assignments = stats['total'] or 0
    crew.rating_average = reviews['avg'] or 0
    crew.rating_count = reviews['total'] or 0
    crew.save(update_fields=('completed_assignments', 'rating_average', 'rating_count', 'updated_at'))


def _refresh_supplier_score(supplier):
    stats = SupplierReview.objects.filter(service_order__supplier=supplier).aggregate(
        avg=Avg('overall'), total=Count('id')
    )
    supplier.rating_average = stats['avg'] or 0
    supplier.rating_count = stats['total'] or 0
    supplier.save(update_fields=('rating_average', 'rating_count', 'updated_at'))


@operations_required
def resource_dashboard(request):
    today = timezone.now()
    tours = Tour.objects.filter(end_date__gte=today.date()).annotate(
        crew_need_count=Count('crew_opportunities', distinct=True),
        crew_booked_count=Count(
            'crew_engagements', filter=Q(crew_engagements__status__in=CrewEngagement.ACTIVE_STATUSES), distinct=True,
        ),
        service_need_count=Count('service_requirements', distinct=True),
        service_order_count=Count('service_orders', distinct=True),
    ).order_by('start_date')[:12]
    return render(request, 'operations/resources/dashboard.html', {
        'tours': tours,
        'approved_crew': CrewMember.objects.filter(verification_status='approved').count(),
        'pending_crew': CrewMember.objects.exclude(verification_status__in=('approved', 'rejected')).count(),
        'open_opportunities': CrewOpportunity.objects.filter(status='published', application_deadline__gt=today).count(),
        'pending_applications': CrewApplication.objects.filter(status__in=('submitted', 'under_review', 'shortlisted')).count(),
        'active_engagements': CrewEngagement.objects.filter(status__in=CrewEngagement.ACTIVE_STATUSES).count(),
        'active_suppliers': ServiceSupplier.objects.filter(status__in=('approved', 'active')).count(),
        'open_rfqs': RequestForQuote.objects.filter(status='published', deadline__gt=today).count(),
        'unpaid_crew': CrewPayment.objects.exclude(status='paid').count(),
        'unpaid_invoices': SupplierInvoice.objects.exclude(status='paid').count(),
    })


@operations_required
def employee_list(request):
    if not can_record_manual_payment(request.user):
        raise PermissionDenied
    employees = EmployeeProfile.objects.select_related('user', 'manager__user').order_by('-is_active', 'department', 'user__first_name')
    return render(request, 'operations/employees/list.html', {'employees': employees})


@operations_required
def employee_form(request, employee_id=None):
    if not can_record_manual_payment(request.user):
        raise PermissionDenied
    instance = get_object_or_404(EmployeeProfile, pk=employee_id) if employee_id else None
    form = EmployeeProfileForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Employee record saved.')
        return redirect('tour:operations:employee_list')
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Employee record', 'back_url': reverse('tour:operations:employee_list')
    })


@operations_required
def crew_list(request):
    crew = CrewMember.objects.select_related('user').prefetch_related('roles').order_by('-created_at')
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    role = request.GET.get('role', '').strip()
    if query:
        crew = crew.filter(Q(display_name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query))
    if status:
        crew = crew.filter(verification_status=status)
    if role:
        crew = crew.filter(qualifications__role__code=role, qualifications__is_active=True)
    page_obj = Paginator(crew.distinct(), 24).get_page(request.GET.get('page'))
    return render(request, 'operations/crew/list.html', {
        'crew_members': page_obj.object_list, 'page_obj': page_obj, 'query': query,
        'selected_status': status, 'selected_role': role,
    })


@operations_required
def crew_detail(request, crew_id):
    crew = get_object_or_404(CrewMember.objects.select_related('user', 'approved_by'), pk=crew_id)
    if request.method == 'POST':
        form = CrewOpsProfileForm(request.POST, instance=crew)
        if form.is_valid():
            previous = crew.verification_status
            crew = form.save(commit=False)
            if crew.verification_status == 'approved' and previous != 'approved':
                crew.approved_by = request.user
                crew.approved_at = timezone.now()
                _notify(crew, 'Profile approved', 'Your tour workforce profile is approved. You can now apply for opportunities.')
            crew.save()
            messages.success(request, 'Crew verification status updated.')
            return redirect('tour:operations:crew_detail', crew_id=crew.pk)
    else:
        form = CrewOpsProfileForm(instance=crew)
    return render(request, 'operations/crew/detail.html', {
        'crew_record': crew, 'status_form': form,
        'applications': crew.applications.select_related('opportunity__tour', 'opportunity__role')[:10],
        'engagements': crew.engagements.select_related('tour', 'role').order_by('-start_at')[:10],
        'training_records': crew.training_records.select_related('course'),
    })


@operations_required
def crew_document_review(request, document_id):
    document = get_object_or_404(CrewDocument, pk=document_id)
    form = CrewDocumentReviewForm(request.POST or None, instance=document)
    if request.method == 'POST' and form.is_valid():
        document = form.save(commit=False)
        document.reviewed_by = request.user
        document.reviewed_at = timezone.now()
        document.save()
        messages.success(request, 'Document review saved.')
        return redirect('tour:operations:crew_detail', crew_id=document.crew_id)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Review crew document',
        'back_url': reverse('tour:operations:crew_detail', args=[document.crew_id]),
    })


@operations_required
@require_POST
def crew_qualification_verify(request, qualification_id):
    qualification = get_object_or_404(CrewQualification, pk=qualification_id)
    qualification.is_verified = request.POST.get('verified') == '1'
    qualification.save(update_fields=('is_verified',))
    messages.success(request, 'Role verification updated.')
    return redirect('tour:operations:crew_detail', crew_id=qualification.crew_id)


@operations_required
def opportunity_list(request):
    opportunities = CrewOpportunity.objects.select_related('tour', 'role').annotate(
        application_count=Count('applications'), engagement_count=Count('engagements')
    ).order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        opportunities = opportunities.filter(status=status)
    return render(request, 'operations/opportunities/list.html', {'opportunities': opportunities, 'selected_status': status})


@operations_required
def opportunity_form(request, opportunity_id=None, tour_id=None):
    instance = get_object_or_404(CrewOpportunity, pk=opportunity_id) if opportunity_id else None
    initial = {'tour': tour_id} if tour_id else {}
    form = CrewOpportunityForm(request.POST or None, instance=instance, initial=initial)
    if request.method == 'POST' and form.is_valid():
        opportunity = form.save(commit=False)
        if not opportunity.pk:
            opportunity.created_by = request.user
        if opportunity.status == 'published' and opportunity.published_at is None:
            opportunity.published_at = timezone.now()
        opportunity.save()
        if opportunity.status == 'published':
            eligible = CrewMember.objects.filter(
                verification_status='approved', available_for_work=True,
                qualifications__role=opportunity.role, qualifications__is_active=True,
                qualifications__is_verified=True,
            ).distinct()
            for crew in eligible:
                if not CrewNotification.objects.filter(
                    crew=crew, title=opportunity.title, url__contains=f'/opportunities/{opportunity.pk}/'
                ).exists():
                    _notify(
                        crew, opportunity.title,
                        f'New {opportunity.role.name} opportunity for {opportunity.tour.title}.',
                        reverse('tour:crew:opportunity_detail', args=[opportunity.pk]),
                    )
        messages.success(request, 'Work opportunity saved.')
        return redirect('tour:operations:opportunity_detail', opportunity_id=opportunity.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Tour workforce opportunity',
        'back_url': reverse('tour:operations:opportunity_list'),
    })


@operations_required
def opportunity_detail(request, opportunity_id):
    opportunity = get_object_or_404(CrewOpportunity.objects.select_related('tour', 'role'), pk=opportunity_id)
    applications = opportunity.applications.select_related('crew', 'reviewed_by').prefetch_related('offers')
    return render(request, 'operations/opportunities/detail.html', {
        'opportunity': opportunity, 'applications': applications,
        'accepted_count': opportunity.engagements.exclude(status='cancelled').count(),
    })


@operations_required
def application_review(request, application_id):
    application = get_object_or_404(CrewApplication.objects.select_related('opportunity', 'crew'), pk=application_id)
    form = CrewApplicationReviewForm(request.POST or None, instance=application)
    if request.method == 'POST' and form.is_valid():
        application = form.save(commit=False)
        application.reviewed_by = request.user
        application.save()
        _notify(application.crew, 'Application updated', f'Your application for {application.opportunity.title} is now {application.get_status_display()}.')
        messages.success(request, 'Application status updated.')
        return redirect('tour:operations:opportunity_detail', opportunity_id=application.opportunity_id)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': f'Review application · {application.crew}',
        'back_url': reverse('tour:operations:opportunity_detail', args=[application.opportunity_id]),
    })


@operations_required
def offer_create(request, application_id):
    application = get_object_or_404(CrewApplication.objects.select_related('opportunity', 'crew'), pk=application_id)
    opportunity = application.opportunity
    latest = application.offers.order_by('-version').first()
    initial = {
        'compensation_type': opportunity.compensation_type,
        'amount': application.proposed_amount or opportunity.budget_max or opportunity.budget_min,
        'currency': opportunity.currency, 'start_at': opportunity.start_at,
        'end_at': opportunity.end_at, 'expires_at': timezone.now() + timedelta(days=3),
        'terms': opportunity.duties,
    }
    if latest:
        for name in ('compensation_type', 'amount', 'currency', 'bonus_amount', 'expense_allowance', 'start_at', 'end_at', 'terms', 'cancellation_terms', 'expires_at'):
            initial[name] = getattr(latest, name)
    form = CrewOfferForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        offer = form.save(commit=False)
        offer.application = application
        offer.version = (latest.version + 1) if latest else 1
        offer.status = 'sent'
        offer.sent_by = request.user
        offer.save()
        application.status = 'offer_sent'
        application.reviewed_by = request.user
        application.save(update_fields=('status', 'reviewed_by', 'updated_at'))
        opportunity.status = 'offer_sent'
        opportunity.save(update_fields=('status', 'updated_at'))
        _notify(
            application.crew, 'Work offer received',
            f'You received an offer for {opportunity.title}.',
            reverse('tour:crew:offer_detail', args=[offer.pk]),
        )
        messages.success(request, 'Offer sent to the crew member.')
        return redirect('tour:operations:opportunity_detail', opportunity_id=opportunity.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': f'Offer · {application.crew}',
        'back_url': reverse('tour:operations:opportunity_detail', args=[opportunity.pk]),
    })


@operations_required
def engagement_list(request):
    engagements = CrewEngagement.objects.select_related('tour', 'crew', 'role').order_by('-start_at')
    status = request.GET.get('status', '')
    if status:
        engagements = engagements.filter(status=status)
    return render(request, 'operations/engagements/list.html', {
        'engagements': engagements, 'selected_status': status,
    })


@operations_required
def engagement_form(request, engagement_id=None, tour_id=None):
    instance = get_object_or_404(CrewEngagement, pk=engagement_id) if engagement_id else None
    form = CrewEngagementForm(request.POST or None, instance=instance, initial={'tour': tour_id} if tour_id else None)
    if request.method == 'POST' and form.is_valid():
        engagement = form.save(commit=False)
        if not engagement.pk:
            engagement.created_by = request.user
        engagement.save()
        messages.success(request, 'Crew booking saved.')
        return redirect('tour:operations:engagement_detail', engagement_id=engagement.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Crew booking', 'back_url': reverse('tour:operations:engagement_list'),
    })


@operations_required
def engagement_detail(request, engagement_id):
    engagement = get_object_or_404(
        CrewEngagement.objects.select_related('tour', 'crew', 'role', 'opportunity'), pk=engagement_id
    )
    status_form = CrewEngagementStatusForm(prefix='status', instance=engagement)
    payment = _related_or_none(engagement, 'payment')
    if payment is None:
        payment = CrewPayment(
            engagement=engagement, base_amount=engagement.agreed_amount,
            bonus_amount=engagement.bonus_amount, currency=engagement.currency,
        )
    payment_form = CrewPaymentForm(prefix='payment', instance=payment)
    review_form = None if hasattr(engagement, 'operations_review') else CrewReviewForm(prefix='review')
    return render(request, 'operations/engagements/detail.html', {
        'engagement': engagement, 'status_form': status_form,
        'payment': _related_or_none(engagement, 'payment'), 'payment_form': payment_form,
        'review_form': review_form,
    })


@operations_required
@require_POST
def engagement_status(request, engagement_id):
    engagement = get_object_or_404(CrewEngagement, pk=engagement_id)
    form = CrewEngagementStatusForm(request.POST, prefix='status', instance=engagement)
    if form.is_valid():
        engagement = form.save(commit=False)
        now = timezone.now()
        if engagement.status == 'completed' and engagement.completed_at is None:
            engagement.completed_at = now
        if engagement.status == 'checked_in' and engagement.checked_in_at is None:
            engagement.checked_in_at = now
        engagement.save()
        _refresh_crew_score(engagement.crew)
        messages.success(request, 'Crew booking status updated.')
    else:
        messages.error(request, 'Please correct the crew booking status form.')
    return redirect('tour:operations:engagement_detail', engagement_id=engagement.pk)


@operations_required
@require_POST
def engagement_payment(request, engagement_id):
    if not can_record_manual_payment(request.user):
        raise PermissionDenied
    engagement = get_object_or_404(CrewEngagement, pk=engagement_id)
    payment = _related_or_none(engagement, 'payment') or CrewPayment(engagement=engagement)
    form = CrewPaymentForm(request.POST, request.FILES, prefix='payment', instance=payment)
    if form.is_valid():
        payment = form.save(commit=False)
        if payment.status in {'approved', 'paid'}:
            payment.approved_by = request.user
        if payment.status == 'paid' and payment.paid_at is None:
            payment.paid_at = timezone.now()
        payment.save()
        _notify(engagement.crew, 'Payment updated', f'Payment for {engagement.tour.title} is now {payment.get_status_display()}.')
        messages.success(request, 'Crew payment record saved.')
    else:
        messages.error(request, 'Please correct the payment form.')
    return redirect('tour:operations:engagement_detail', engagement_id=engagement.pk)


@operations_required
@require_POST
def engagement_review(request, engagement_id):
    engagement = get_object_or_404(CrewEngagement, pk=engagement_id)
    form = CrewReviewForm(request.POST, prefix='review')
    if form.is_valid():
        CrewReview.objects.update_or_create(
            engagement=engagement, reviewer=request.user, reviewer_type='operations',
            defaults=form.cleaned_data,
        )
        _refresh_crew_score(engagement.crew)
        messages.success(request, 'Operations review saved.')
    else:
        messages.error(request, 'Please correct the review form.')
    return redirect('tour:operations:engagement_detail', engagement_id=engagement.pk)


@operations_required
def training_list(request):
    courses = TrainingCourse.objects.prefetch_related('required_for_roles').annotate(record_count=Count('crew_records'))
    return render(request, 'operations/training/list.html', {'courses': courses})


@operations_required
def training_course_form(request, course_id=None):
    instance = get_object_or_404(TrainingCourse, pk=course_id) if course_id else None
    form = TrainingCourseForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        course = form.save()
        messages.success(request, 'Training course saved.')
        return redirect('tour:operations:training_list')
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Training course', 'back_url': reverse('tour:operations:training_list'),
    })


@operations_required
def training_record_form(request, record_id=None, crew_id=None):
    instance = get_object_or_404(CrewTrainingRecord, pk=record_id) if record_id else None
    form = CrewTrainingRecordForm(request.POST or None, request.FILES or None, instance=instance, initial={'crew': crew_id} if crew_id else None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.verified_by = request.user
        record.save()
        messages.success(request, 'Training record saved.')
        return redirect('tour:operations:crew_detail', crew_id=record.crew_id)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Crew training record',
        'back_url': reverse('tour:operations:crew_list'),
    })


@operations_required
def case_list(request):
    cases = CrewCase.objects.select_related('crew', 'engagement__tour', 'assigned_to').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        cases = cases.filter(status=status)
    return render(request, 'operations/cases/list.html', {'cases': cases, 'selected_status': status})


@operations_required
def case_detail(request, case_id):
    case = get_object_or_404(CrewCase.objects.select_related('crew', 'engagement__tour', 'created_by'), pk=case_id)
    form = CrewCaseResolutionForm(request.POST or None, instance=case)
    if request.method == 'POST' and form.is_valid():
        form.save()
        _notify(case.crew, 'Case updated', f'Case #{case.pk} is now {case.get_status_display()}.')
        messages.success(request, 'Case updated.')
        return redirect('tour:operations:case_detail', case_id=case.pk)
    return render(request, 'operations/cases/detail.html', {'case_record': case, 'form': form})


@operations_required
def supplier_list(request):
    suppliers = ServiceSupplier.objects.prefetch_related('categories').annotate(
        active_contracts=Count('contracts', filter=Q(contracts__status='active'), distinct=True),
        order_count=Count('service_orders', distinct=True),
    ).order_by('-created_at')
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    if query:
        suppliers = suppliers.filter(Q(legal_name__icontains=query) | Q(trading_name__icontains=query) | Q(contact_name__icontains=query))
    if status:
        suppliers = suppliers.filter(status=status)
    return render(request, 'operations/suppliers/list.html', {
        'suppliers': suppliers, 'query': query, 'selected_status': status,
    })


@operations_required
def supplier_form(request, supplier_id=None):
    instance = get_object_or_404(ServiceSupplier, pk=supplier_id) if supplier_id else None
    form = SupplierOpsForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        supplier = form.save(commit=False)
        if supplier.status in {'approved', 'active'} and supplier.approved_at is None:
            supplier.approved_by = request.user
            supplier.approved_at = timezone.now()
        supplier.save()
        form.save_m2m()
        messages.success(request, 'Supplier record saved.')
        return redirect('tour:operations:supplier_detail', supplier_id=supplier.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Service supplier', 'back_url': reverse('tour:operations:supplier_list'),
    })


@operations_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(ServiceSupplier.objects.prefetch_related('categories'), pk=supplier_id)
    return render(request, 'operations/suppliers/detail.html', {
        'supplier_record': supplier,
        'orders': supplier.service_orders.select_related('tour').order_by('-start_at')[:10],
    })


def _supplier_child_form(request, supplier_id, form_class, title, success_message):
    supplier = get_object_or_404(ServiceSupplier, pk=supplier_id)
    form = form_class(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.supplier = supplier
        instance.save()
        if hasattr(form, 'save_m2m'):
            form.save_m2m()
        messages.success(request, success_message)
        return redirect('tour:operations:supplier_detail', supplier_id=supplier.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': title, 'back_url': reverse('tour:operations:supplier_detail', args=[supplier.pk]),
    })


@operations_required
def supplier_service_form(request, supplier_id):
    return _supplier_child_form(request, supplier_id, SupplierServiceForm, 'Supplier service', 'Service saved.')


@operations_required
def supplier_asset_form(request, supplier_id):
    return _supplier_child_form(request, supplier_id, SupplierAssetForm, 'Supplier asset', 'Asset saved.')


@operations_required
def supplier_document_form(request, supplier_id):
    return _supplier_child_form(request, supplier_id, SupplierDocumentForm, 'Supplier document', 'Document uploaded.')


@operations_required
@require_POST
def supplier_document_verify(request, document_id):
    document = get_object_or_404(SupplierDocument, pk=document_id)
    document.is_verified = request.POST.get('verified') == '1'
    document.save(update_fields=('is_verified',))
    messages.success(request, 'Supplier document verification updated.')
    return redirect('tour:operations:supplier_detail', supplier_id=document.supplier_id)


@operations_required
def supplier_contract_form(request, supplier_id):
    supplier = get_object_or_404(ServiceSupplier, pk=supplier_id)
    form = SupplierContractForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        contract = form.save(commit=False)
        contract.supplier = supplier
        if contract.status in {'signed', 'active'}:
            contract.approved_by = request.user
            if contract.signed_at is None:
                contract.signed_at = timezone.now()
        contract.save()
        messages.success(request, 'Supplier contract saved.')
        return redirect('tour:operations:supplier_detail', supplier_id=supplier.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Supplier master contract',
        'back_url': reverse('tour:operations:supplier_detail', args=[supplier.pk]),
    })


@operations_required
def supplier_rate_form(request, contract_id):
    contract = get_object_or_404(SupplierContract.objects.select_related('supplier'), pk=contract_id)
    form = SupplierRateForm(request.POST or None, supplier=contract.supplier)
    if request.method == 'POST' and form.is_valid():
        rate = form.save(commit=False)
        rate.contract = contract
        rate.save()
        messages.success(request, 'Contract rate saved.')
        return redirect('tour:operations:supplier_detail', supplier_id=contract.supplier_id)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': 'Contract rate',
        'back_url': reverse('tour:operations:supplier_detail', args=[contract.supplier_id]),
    })


@operations_required
def tour_resources(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    opportunities = tour.crew_opportunities.select_related('role').annotate(
        application_count=Count('applications'), booked_count=Count('engagements')
    )
    engagements = tour.crew_engagements.select_related('crew', 'role')
    requirements = tour.service_requirements.select_related('category')
    orders = tour.service_orders.select_related('supplier')
    totals = {}

    def money_row(currency):
        return totals.setdefault(currency or 'USD', {
            'currency': currency or 'USD', 'crew_committed': Decimal('0'),
            'supplier_committed': Decimal('0'), 'crew_paid': Decimal('0'),
            'supplier_paid': Decimal('0'),
        })

    crew_costs = engagements.exclude(status='cancelled').values('currency').annotate(
        agreed=Sum('agreed_amount'), bonus=Sum('bonus_amount'), expense=Sum('expense_allowance')
    )
    for cost in crew_costs:
        money_row(cost['currency'])['crew_committed'] = sum(
            (cost.get(field) or Decimal('0')) for field in ('agreed', 'bonus', 'expense')
        )
    for cost in orders.exclude(status='cancelled').values('currency').annotate(total=Sum('total_amount')):
        money_row(cost['currency'])['supplier_committed'] = cost['total'] or Decimal('0')
    for cost in CrewPayment.objects.filter(
        engagement__tour=tour, status='paid'
    ).values('currency').annotate(total=Sum('net_amount')):
        money_row(cost['currency'])['crew_paid'] = cost['total'] or Decimal('0')
    for cost in SupplierInvoice.objects.filter(
        service_order__tour=tour, status='paid'
    ).values('currency').annotate(total=Sum('amount')):
        money_row(cost['currency'])['supplier_paid'] = cost['total'] or Decimal('0')

    financial_rows = []
    for currency in sorted(totals):
        row = totals[currency]
        row['total_committed'] = row['crew_committed'] + row['supplier_committed']
        row['total_paid'] = row['crew_paid'] + row['supplier_paid']
        financial_rows.append(row)
    return render(request, 'operations/tours/resources.html', {
        'tour': tour, 'opportunities': opportunities, 'engagements': engagements,
        'requirements': requirements, 'orders': orders, 'financial_rows': financial_rows,
    })


@operations_required
def requirement_form(request, tour_id, requirement_id=None):
    tour = get_object_or_404(Tour, pk=tour_id)
    instance = get_object_or_404(ServiceRequirement, pk=requirement_id, tour=tour) if requirement_id else None
    form = ServiceRequirementForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        requirement = form.save(commit=False)
        requirement.tour = tour
        if not requirement.pk:
            requirement.created_by = request.user
        requirement.save()
        messages.success(request, 'Tour service requirement saved.')
        return redirect('tour:operations:tour_resources', tour_id=tour.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': f'Service requirement · {tour.title}',
        'back_url': reverse('tour:operations:tour_resources', args=[tour.pk]),
    })


@operations_required
def rfq_list(request):
    rfqs = RequestForQuote.objects.select_related('requirement__tour', 'requirement__category').annotate(
        quote_count=Count('quotes')
    ).order_by('-created_at')
    return render(request, 'operations/procurement/rfq_list.html', {'rfqs': rfqs})


@operations_required
def rfq_form(request, requirement_id):
    requirement = get_object_or_404(ServiceRequirement.objects.select_related('tour'), pk=requirement_id)
    instance = _related_or_none(requirement, 'rfq')
    initial = {
        'reference': f'RFQ-{requirement.tour_id}-{requirement.pk}',
        'deadline': requirement.needed_by,
    }
    form = RFQForm(request.POST or None, instance=instance, initial=initial)
    if request.method == 'POST' and form.is_valid():
        rfq = form.save(commit=False)
        rfq.requirement = requirement
        if not rfq.pk:
            rfq.created_by = request.user
        if rfq.status == 'published' and rfq.published_at is None:
            rfq.published_at = timezone.now()
        rfq.save()
        requirement.status = 'sourcing'
        requirement.save(update_fields=('status',))
        messages.success(request, 'Request for quotation saved.')
        return redirect('tour:operations:rfq_detail', rfq_id=rfq.pk)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': f'RFQ · {requirement.title}',
        'back_url': reverse('tour:operations:tour_resources', args=[requirement.tour_id]),
    })


@operations_required
def rfq_detail(request, rfq_id):
    rfq = get_object_or_404(RequestForQuote.objects.select_related('requirement__tour', 'requirement__category'), pk=rfq_id)
    quotes = rfq.quotes.select_related('supplier').order_by('amount')
    return render(request, 'operations/procurement/rfq_detail.html', {'rfq': rfq, 'quotes': quotes})


@operations_required
@require_POST
def quote_select(request, quote_id):
    with transaction.atomic():
        quote = get_object_or_404(
            SupplierQuote.objects.select_for_update().select_related('rfq__requirement__tour', 'supplier'), pk=quote_id
        )
        rfq = quote.rfq
        requirement = rfq.requirement
        if rfq.status not in {'published', 'closed'}:
            messages.error(request, 'This RFQ cannot be awarded in its current state.')
            return redirect('tour:operations:rfq_detail', rfq_id=rfq.pk)
        quote.status = 'selected'
        quote.save(update_fields=('status', 'updated_at'))
        rfq.quotes.exclude(pk=quote.pk).update(status='rejected')
        rfq.status = 'awarded'
        rfq.save(update_fields=('status',))
        requirement.status = 'contracted'
        requirement.save(update_fields=('status',))
        contract = quote.supplier.contracts.filter(
            status='active', start_date__lte=requirement.start_at.date(),
            end_date__gte=requirement.end_at.date(),
        ).first()
        order_number = f'SO-{requirement.tour_id}-{requirement.pk}-{quote.pk}'
        order, _ = ServiceOrder.objects.get_or_create(
            quote=quote,
            defaults={
                'order_number': order_number, 'tour': requirement.tour,
                'requirement': requirement, 'supplier': quote.supplier, 'contract': contract,
                'description': requirement.description, 'start_at': requirement.start_at,
                'end_at': requirement.end_at, 'quantity': requirement.quantity,
                'unit': requirement.unit,
                'unit_price': quote.amount / requirement.quantity if requirement.quantity else quote.amount,
                'total_amount': quote.amount, 'currency': quote.currency,
                'status': 'issued', 'cancellation_terms': quote.cancellation_terms,
                'created_by': request.user, 'approved_by': request.user,
            },
        )
    messages.success(request, f'Quote selected and service order {order.order_number} issued.')
    return redirect('tour:operations:service_order_detail', order_id=order.pk)


@operations_required
def service_order_list(request):
    orders = ServiceOrder.objects.select_related('tour', 'supplier', 'requirement').order_by('-start_at')
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    return render(request, 'operations/procurement/order_list.html', {'orders': orders, 'selected_status': status})


@operations_required
def service_order_detail(request, order_id):
    order = get_object_or_404(ServiceOrder.objects.select_related('tour', 'supplier', 'contract', 'quote'), pk=order_id)
    return render(request, 'operations/procurement/order_detail.html', {
        'order': order, 'status_form': ServiceOrderStatusForm(prefix='status', instance=order),
        'invoices': order.invoices.all(),
        'review_form': None if _related_or_none(order, 'review') else SupplierReviewForm(prefix='review'),
    })


@operations_required
@require_POST
def service_order_status(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id)
    form = ServiceOrderStatusForm(request.POST, request.FILES, prefix='status', instance=order)
    if form.is_valid():
        order = form.save()
        if order.requirement_id:
            mapped = {'confirmed': 'confirmed', 'delivered': 'delivered', 'completed': 'completed', 'cancelled': 'cancelled'}
            if order.status in mapped:
                ServiceRequirement.objects.filter(pk=order.requirement_id).update(status=mapped[order.status])
        messages.success(request, 'Service order updated.')
    else:
        messages.error(request, 'Please correct the service order form.')
    return redirect('tour:operations:service_order_detail', order_id=order.pk)


@operations_required
def invoice_review(request, invoice_id):
    if not can_record_manual_payment(request.user):
        raise PermissionDenied
    invoice = get_object_or_404(SupplierInvoice.objects.select_related('service_order'), pk=invoice_id)
    form = SupplierInvoiceReviewForm(request.POST or None, instance=invoice)
    if request.method == 'POST' and form.is_valid():
        invoice = form.save(commit=False)
        if invoice.status == 'paid' and invoice.paid_at is None:
            invoice.paid_at = timezone.now()
        invoice.save()
        messages.success(request, 'Supplier invoice updated.')
        return redirect('tour:operations:service_order_detail', order_id=invoice.service_order_id)
    return render(request, 'operations/resources/form.html', {
        'form': form, 'title': f'Invoice {invoice.invoice_number}',
        'back_url': reverse('tour:operations:service_order_detail', args=[invoice.service_order_id]),
    })


@operations_required
@require_POST
def supplier_review(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id)
    form = SupplierReviewForm(request.POST, prefix='review')
    if form.is_valid():
        SupplierReview.objects.update_or_create(service_order=order, defaults={'reviewer': request.user, **form.cleaned_data})
        _refresh_supplier_score(order.supplier)
        messages.success(request, 'Supplier performance review saved.')
    else:
        messages.error(request, 'Please correct the supplier review form.')
    return redirect('tour:operations:service_order_detail', order_id=order.pk)


# Crew workforce portal


@login_required
def crew_onboarding(request):
    existing = _related_or_none(request.user, 'crew_profile')
    if existing:
        return redirect('tour:crew:dashboard')
    initial = {
        'display_name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
    }
    form = CrewProfileForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        crew = form.save(commit=False)
        crew.user = request.user
        crew.verification_status = 'submitted'
        crew.save()
        messages.success(request, 'Your workforce profile was submitted. Add your roles and documents next.')
        return redirect('tour:crew:profile')
    return render(request, 'crew/onboarding.html', {'form': form})


@crew_required
def crew_dashboard(request):
    crew = request.crew
    opportunities = list(CrewOpportunity.objects.filter(
        status='published', application_deadline__gt=timezone.now(), start_at__gt=timezone.now(),
    ).select_related('tour', 'role').order_by('start_at')[:12])
    applied_ids = set(crew.applications.values_list('opportunity_id', flat=True))
    for opportunity in opportunities:
        opportunity.eligible, opportunity.eligibility_reasons = _crew_eligibility(crew, opportunity)
        opportunity.already_applied = opportunity.pk in applied_ids
    return render(request, 'crew/dashboard.html', {
        'crew': crew, 'opportunities': opportunities,
        'active_engagements': crew.engagements.filter(status__in=CrewEngagement.ACTIVE_STATUSES).order_by('start_at')[:5],
        'pending_applications': crew.applications.exclude(status__in=('accepted', 'rejected', 'withdrawn', 'expired')).count(),
        'pending_offers': CrewOffer.objects.filter(application__crew=crew, status='sent', expires_at__gt=timezone.now()).count(),
        'unread_notifications': crew.notifications.filter(read_at__isnull=True)[:8],
    })


@crew_required
def crew_profile(request):
    crew = request.crew
    form = CrewProfileForm(request.POST or None, request.FILES or None, instance=crew)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your workforce profile was updated.')
        return redirect('tour:crew:profile')
    return render(request, 'crew/profile.html', {
        'crew': crew, 'form': form,
        'qualification_form': CrewQualificationForm(prefix='qualification'),
        'document_form': CrewDocumentForm(prefix='document'),
        'availability_form': CrewAvailabilityForm(prefix='availability'),
    })


@crew_required
@require_POST
def crew_qualification_add(request):
    form = CrewQualificationForm(request.POST, prefix='qualification')
    if form.is_valid():
        qualification = form.save(commit=False)
        qualification.crew = request.crew
        qualification.is_verified = False
        try:
            qualification.save()
            messages.success(request, 'Role added and sent for verification.')
        except Exception:
            messages.error(request, 'This role is already on your profile.')
    else:
        messages.error(request, 'Please correct the role form.')
    return redirect('tour:crew:profile')


@crew_required
@require_POST
def crew_document_add(request):
    form = CrewDocumentForm(request.POST, request.FILES, prefix='document')
    if form.is_valid():
        document = form.save(commit=False)
        document.crew = request.crew
        document.save()
        messages.success(request, 'Document uploaded for verification.')
    else:
        messages.error(request, 'Please correct the document form.')
    return redirect('tour:crew:profile')


@crew_required
@require_POST
def crew_availability_add(request):
    form = CrewAvailabilityForm(request.POST, prefix='availability')
    if form.is_valid():
        block = form.save(commit=False)
        block.crew = request.crew
        block.save()
        messages.success(request, 'Availability calendar updated.')
    else:
        messages.error(request, 'Please correct the availability form.')
    return redirect('tour:crew:profile')


@crew_required
def crew_opportunity_list(request):
    opportunities = list(CrewOpportunity.objects.filter(
        status='published', application_deadline__gt=timezone.now(),
    ).select_related('tour', 'role').order_by('start_at'))
    applied_ids = set(request.crew.applications.values_list('opportunity_id', flat=True))
    for opportunity in opportunities:
        opportunity.eligible, opportunity.eligibility_reasons = _crew_eligibility(request.crew, opportunity)
        opportunity.already_applied = opportunity.pk in applied_ids
    return render(request, 'crew/opportunities.html', {'crew': request.crew, 'opportunities': opportunities})


@crew_required
def crew_opportunity_detail(request, opportunity_id):
    opportunity = get_object_or_404(CrewOpportunity.objects.select_related('tour', 'role'), pk=opportunity_id)
    eligible, reasons = _crew_eligibility(request.crew, opportunity)
    application = request.crew.applications.filter(opportunity=opportunity).first()
    form = CrewApplicationForm()
    return render(request, 'crew/opportunity_detail.html', {
        'crew': request.crew, 'opportunity': opportunity, 'eligible': eligible,
        'eligibility_reasons': reasons, 'application': application, 'form': form,
    })


@crew_required
@require_POST
def crew_apply(request, opportunity_id):
    opportunity = get_object_or_404(CrewOpportunity, pk=opportunity_id)
    eligible, reasons = _crew_eligibility(request.crew, opportunity)
    if not opportunity.is_open:
        messages.error(request, 'Applications are closed for this opportunity.')
    elif not eligible:
        messages.error(request, 'You are not eligible: ' + ' '.join(reasons))
    elif request.crew.applications.filter(opportunity=opportunity).exists():
        messages.info(request, 'You have already applied for this opportunity.')
    else:
        form = CrewApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.opportunity = opportunity
            application.crew = request.crew
            application.save()
            messages.success(request, 'Your application was submitted.')
            return redirect('tour:crew:applications')
        messages.error(request, 'Please correct the application form.')
    return redirect('tour:crew:opportunity_detail', opportunity_id=opportunity.pk)


@crew_required
def crew_applications(request):
    applications = request.crew.applications.select_related('opportunity__tour', 'opportunity__role').prefetch_related('offers')
    return render(request, 'crew/applications.html', {'crew': request.crew, 'applications': applications})


@crew_required
def crew_offer_detail(request, offer_id):
    offer = get_object_or_404(
        CrewOffer.objects.select_related('application__opportunity__tour', 'application__crew'),
        pk=offer_id, application__crew=request.crew,
    )
    return render(request, 'crew/offer_detail.html', {'crew': request.crew, 'offer': offer})


@crew_required
@require_POST
def crew_offer_response(request, offer_id):
    action = request.POST.get('action')
    with transaction.atomic():
        offer = get_object_or_404(
            CrewOffer.objects.select_for_update().select_related('application__opportunity__tour', 'application__crew'),
            pk=offer_id, application__crew=request.crew,
        )
        if offer.status != 'sent' or offer.expires_at <= timezone.now():
            messages.error(request, 'This offer is no longer available.')
            return redirect('tour:crew:offer_detail', offer_id=offer.pk)
        application = offer.application
        opportunity = CrewOpportunity.objects.select_for_update().get(pk=application.opportunity_id)
        if action == 'decline':
            offer.status = 'declined'
            offer.responded_at = timezone.now()
            offer.save(update_fields=('status', 'responded_at'))
            application.status = 'negotiation'
            application.save(update_fields=('status', 'updated_at'))
            messages.info(request, 'Offer declined. Operations can review your application again.')
        elif action == 'accept':
            if opportunity.engagements.exclude(status='cancelled').count() >= opportunity.positions:
                messages.error(request, 'All available positions have already been filled.')
                return redirect('tour:crew:offer_detail', offer_id=offer.pk)
            engagement = CrewEngagement(
                tour=opportunity.tour, opportunity=opportunity, application=application,
                offer=offer, crew=request.crew, role=opportunity.role,
                start_at=offer.start_at, end_at=offer.end_at,
                compensation_type=offer.compensation_type, agreed_amount=offer.amount,
                currency=offer.currency, bonus_amount=offer.bonus_amount,
                expense_allowance=offer.expense_allowance, duties=opportunity.duties,
                cancellation_terms=offer.cancellation_terms, status='confirmed',
                accepted_at=timezone.now(), created_by=offer.sent_by,
            )
            try:
                engagement.full_clean()
                engagement.save()
            except ValidationError as exc:
                messages.error(request, 'The dates conflict with another confirmed booking: ' + ' '.join(exc.messages))
                return redirect('tour:crew:offer_detail', offer_id=offer.pk)
            offer.status = 'accepted'
            offer.responded_at = timezone.now()
            offer.save(update_fields=('status', 'responded_at'))
            application.status = 'accepted'
            application.save(update_fields=('status', 'updated_at'))
            if opportunity.engagements.exclude(status='cancelled').count() >= opportunity.positions:
                opportunity.status = 'filled'
                opportunity.save(update_fields=('status', 'updated_at'))
            messages.success(request, 'Offer accepted. The assignment is booked in your calendar.')
            return redirect('tour:crew:engagement_detail', engagement_id=engagement.pk)
        else:
            messages.error(request, 'Unknown offer action.')
    return redirect('tour:crew:offer_detail', offer_id=offer.pk)


@crew_required
def crew_engagements(request):
    engagements = request.crew.engagements.select_related('tour', 'role').order_by('-start_at')
    return render(request, 'crew/engagements.html', {'crew': request.crew, 'engagements': engagements})


@crew_required
def crew_engagement_detail(request, engagement_id):
    engagement = get_object_or_404(
        CrewEngagement.objects.select_related('tour', 'role'), pk=engagement_id, crew=request.crew
    )
    return render(request, 'crew/engagement_detail.html', {
        'crew': request.crew, 'engagement': engagement,
        'payment': _related_or_none(engagement, 'payment'),
    })


@crew_required
@require_POST
def crew_engagement_checkin(request, engagement_id):
    engagement = get_object_or_404(CrewEngagement, pk=engagement_id, crew=request.crew)
    if engagement.status not in {'confirmed', 'booked'}:
        messages.error(request, 'This assignment cannot be checked in now.')
    else:
        engagement.status = 'checked_in'
        engagement.checked_in_at = timezone.now()
        engagement.save(update_fields=('status', 'checked_in_at', 'updated_at'))
        messages.success(request, 'Check-in recorded.')
    return redirect('tour:crew:engagement_detail', engagement_id=engagement.pk)


@crew_required
@require_POST
def crew_engagement_checkout(request, engagement_id):
    engagement = get_object_or_404(CrewEngagement, pk=engagement_id, crew=request.crew)
    if engagement.status not in {'checked_in', 'in_progress'}:
        messages.error(request, 'This assignment cannot be checked out now.')
    else:
        engagement.status = 'in_progress'
        engagement.checked_out_at = timezone.now()
        engagement.save(update_fields=('status', 'checked_out_at', 'updated_at'))
        messages.success(request, 'Check-out recorded. Operations will verify completion.')
    return redirect('tour:crew:engagement_detail', engagement_id=engagement.pk)


@crew_required
def crew_training(request):
    courses = TrainingCourse.objects.filter(is_active=True).prefetch_related('required_for_roles')
    records = {record.course_id: record for record in request.crew.training_records.select_related('course')}
    for course in courses:
        course.crew_record = records.get(course.pk)
    return render(request, 'crew/training.html', {'crew': request.crew, 'courses': courses})


@crew_required
def crew_cases(request):
    return render(request, 'crew/cases.html', {
        'crew': request.crew, 'cases': request.crew.cases.select_related('engagement__tour').order_by('-created_at'),
    })


@crew_required
def crew_case_create(request):
    form = CrewCaseForm(request.POST or None, crew=request.crew)
    if request.method == 'POST' and form.is_valid():
        case = form.save(commit=False)
        case.crew = request.crew
        case.created_by = request.user
        case.save()
        messages.success(request, f'Case #{case.pk} was submitted.')
        return redirect('tour:crew:cases')
    return render(request, 'crew/form.html', {'crew': request.crew, 'form': form, 'title': 'New support case'})


@login_required
def customer_crew_review(request, engagement_id):
    engagement = get_object_or_404(CrewEngagement.objects.select_related('tour', 'crew', 'role'), pk=engagement_id)
    booking = Booking.objects.filter(
        user=request.user, tour=engagement.tour, situation__in=('completed', 'Reviewed')
    ).first()
    if booking is None:
        raise PermissionDenied
    review = CrewReview.objects.filter(
        engagement=engagement, reviewer=request.user, reviewer_type='tourist'
    ).first()
    form = CrewReviewForm(request.POST or None, instance=review)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.engagement = engagement
        review.reviewer = request.user
        review.reviewer_type = 'tourist'
        review.save()
        _refresh_crew_score(engagement.crew)
        messages.success(request, 'Thank you. Your crew review was saved.')
        return redirect('tour:customer_tours')
    return render(request, 'crew/customer_review.html', {'engagement': engagement, 'form': form})


# Supplier portal


@login_required
def supplier_onboarding(request):
    existing = _related_or_none(request.user, 'supplier_profile')
    if existing:
        return redirect('tour:supplier:dashboard')
    initial = {'contact_name': request.user.get_full_name() or request.user.username, 'email': request.user.email}
    form = SupplierProfileForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        supplier = form.save(commit=False)
        supplier.user = request.user
        supplier.status = 'under_review'
        supplier.save()
        form.save_m2m()
        messages.success(request, 'Your supplier profile was submitted for review.')
        return redirect('tour:supplier:profile')
    return render(request, 'supplier_portal/onboarding.html', {'form': form})


def _supplier_open_rfqs(supplier):
    return RequestForQuote.objects.filter(
        status='published', deadline__gt=timezone.now(),
        requirement__category__in=supplier.categories.all(),
    ).select_related('requirement__tour', 'requirement__category').distinct()


@supplier_required
def supplier_dashboard(request):
    supplier = request.supplier
    return render(request, 'supplier_portal/dashboard.html', {
        'supplier': supplier, 'open_rfqs': _supplier_open_rfqs(supplier)[:8],
        'orders': supplier.service_orders.select_related('tour').order_by('-start_at')[:8],
        'unpaid_invoices': SupplierInvoice.objects.filter(service_order__supplier=supplier).exclude(status='paid').count(),
    })


@supplier_required
def supplier_profile(request):
    supplier = request.supplier
    form = SupplierProfileForm(request.POST or None, instance=supplier)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Supplier profile updated.')
        return redirect('tour:supplier:profile')
    return render(request, 'supplier_portal/profile.html', {
        'supplier': supplier, 'form': form,
        'service_form': SupplierServiceForm(prefix='service'),
        'asset_form': SupplierAssetForm(prefix='asset'),
        'document_form': SupplierDocumentForm(prefix='document'),
    })


def _supplier_portal_child(request, form_class, prefix, message):
    form = form_class(request.POST, request.FILES or None, prefix=prefix)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.supplier = request.supplier
        instance.save()
        messages.success(request, message)
    else:
        messages.error(request, 'Please correct the submitted form.')
    return redirect('tour:supplier:profile')


@supplier_required
@require_POST
def supplier_service_add(request):
    return _supplier_portal_child(request, SupplierServiceForm, 'service', 'Service added.')


@supplier_required
@require_POST
def supplier_asset_add(request):
    return _supplier_portal_child(request, SupplierAssetForm, 'asset', 'Asset added.')


@supplier_required
@require_POST
def supplier_document_add(request):
    return _supplier_portal_child(request, SupplierDocumentForm, 'document', 'Document uploaded.')


@supplier_required
def supplier_rfq_list(request):
    return render(request, 'supplier_portal/rfqs.html', {
        'supplier': request.supplier, 'rfqs': _supplier_open_rfqs(request.supplier),
    })


@supplier_required
def supplier_rfq_detail(request, rfq_id):
    rfq = get_object_or_404(_supplier_open_rfqs(request.supplier), pk=rfq_id)
    quote = request.supplier.quotes.filter(rfq=rfq).first()
    form = SupplierQuoteForm(request.POST or None, request.FILES or None, instance=quote)
    if request.method == 'POST':
        if not request.supplier.is_approved:
            messages.error(request, 'Your supplier profile must be approved before quoting.')
        elif not rfq.is_open:
            messages.error(request, 'This RFQ is closed.')
        elif form.is_valid():
            quote = form.save(commit=False)
            quote.rfq = rfq
            quote.supplier = request.supplier
            quote.status = 'submitted'
            quote.save()
            messages.success(request, 'Quotation submitted.')
            return redirect('tour:supplier:rfq_detail', rfq_id=rfq.pk)
    return render(request, 'supplier_portal/rfq_detail.html', {
        'supplier': request.supplier, 'rfq': rfq, 'quote': quote, 'form': form,
    })


@supplier_required
def supplier_order_list(request):
    orders = request.supplier.service_orders.select_related('tour').order_by('-start_at')
    return render(request, 'supplier_portal/orders.html', {'supplier': request.supplier, 'orders': orders})


@supplier_required
def supplier_order_detail(request, order_id):
    order = get_object_or_404(
        ServiceOrder.objects.select_related('tour', 'requirement', 'contract'),
        pk=order_id, supplier=request.supplier,
    )
    return render(request, 'supplier_portal/order_detail.html', {
        'supplier': request.supplier, 'order': order, 'invoices': order.invoices.all(),
        'invoice_form': SupplierInvoiceForm(prefix='invoice'),
    })


@supplier_required
@require_POST
def supplier_order_action(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id, supplier=request.supplier)
    action = request.POST.get('action')
    allowed = {'confirm': 'confirmed', 'start': 'in_service', 'deliver': 'delivered', 'dispute': 'disputed'}
    new_status = allowed.get(action)
    if new_status is None:
        messages.error(request, 'Unknown service order action.')
    else:
        order.status = new_status
        order.save(update_fields=('status', 'updated_at'))
        if order.requirement_id and new_status in {'confirmed', 'delivered'}:
            ServiceRequirement.objects.filter(pk=order.requirement_id).update(status=new_status)
        messages.success(request, f'Service order marked {order.get_status_display()}.')
    return redirect('tour:supplier:order_detail', order_id=order.pk)


@supplier_required
@require_POST
def supplier_invoice_add(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id, supplier=request.supplier)
    form = SupplierInvoiceForm(request.POST, request.FILES, prefix='invoice')
    if form.is_valid():
        invoice = form.save(commit=False)
        invoice.service_order = order
        invoice.status = 'submitted'
        invoice.save()
        messages.success(request, 'Invoice submitted for review.')
    else:
        messages.error(request, 'Please correct the invoice form.')
    return redirect('tour:supplier:order_detail', order_id=order.pk)
