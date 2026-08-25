from django import forms

from .models import (
    CrewApplication,
    CrewAvailability,
    CrewCase,
    CrewDocument,
    CrewEngagement,
    CrewMember,
    CrewOffer,
    CrewOpportunity,
    CrewPayment,
    CrewQualification,
    CrewReview,
    CrewTrainingRecord,
    EmployeeProfile,
    RequestForQuote,
    ServiceOrder,
    ServiceRequirement,
    ServiceSupplier,
    SupplierAsset,
    SupplierContract,
    SupplierDocument,
    SupplierInvoice,
    SupplierQuote,
    SupplierRate,
    SupplierReview,
    SupplierService,
    TrainingCourse,
)


DATETIME_WIDGET = forms.DateTimeInput(
    attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
)
DATE_WIDGET = forms.DateInput(attrs={'type': 'date'})


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'ops-check')
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault('class', 'ops-check-list')
            else:
                field.widget.attrs.setdefault('class', 'ops-input')


class EmployeeProfileForm(StyledModelForm):
    class Meta:
        model = EmployeeProfile
        fields = (
            'user', 'employee_code', 'department', 'job_title', 'employment_type',
            'manager', 'start_date', 'end_date', 'monthly_salary', 'currency',
            'emergency_contact', 'notes', 'is_active',
        )
        widgets = {'start_date': DATE_WIDGET, 'end_date': DATE_WIDGET, 'notes': forms.Textarea(attrs={'rows': 3})}


class CrewProfileForm(StyledModelForm):
    class Meta:
        model = CrewMember
        fields = (
            'display_name', 'phone', 'email', 'gender', 'date_of_birth', 'base_location',
            'service_regions', 'languages', 'bio', 'profile_image', 'available_for_work',
            'default_daily_rate', 'preferred_currency', 'emergency_contact_name',
            'emergency_contact_phone', 'payout_method', 'payout_reference',
        )
        widgets = {
            'date_of_birth': DATE_WIDGET,
            'service_regions': forms.Textarea(attrs={'rows': 2}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class CrewOpsProfileForm(StyledModelForm):
    class Meta:
        model = CrewMember
        fields = ('verification_status', 'available_for_work')


class CrewQualificationForm(StyledModelForm):
    class Meta:
        model = CrewQualification
        fields = ('role', 'experience_years', 'specialties', 'usual_daily_rate', 'is_active')


class CrewDocumentForm(StyledModelForm):
    class Meta:
        model = CrewDocument
        fields = ('document_type', 'title', 'file', 'reference_number', 'issued_at', 'expires_at')
        widgets = {'issued_at': DATE_WIDGET, 'expires_at': DATE_WIDGET}


class CrewDocumentReviewForm(StyledModelForm):
    class Meta:
        model = CrewDocument
        fields = ('review_status', 'review_note')
        widgets = {'review_note': forms.Textarea(attrs={'rows': 2})}


class CrewAvailabilityForm(StyledModelForm):
    class Meta:
        model = CrewAvailability
        fields = ('start_at', 'end_at', 'availability_type', 'note')
        widgets = {'start_at': DATETIME_WIDGET, 'end_at': DATETIME_WIDGET}


class CrewOpportunityForm(StyledModelForm):
    class Meta:
        model = CrewOpportunity
        fields = (
            'tour', 'role', 'title', 'summary', 'duties', 'requirements', 'location',
            'start_at', 'end_at', 'positions', 'minimum_experience_years',
            'required_languages', 'compensation_type', 'currency', 'budget_min',
            'budget_max', 'accommodation_included', 'meals_included',
            'transport_included', 'application_deadline', 'status',
        )
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'duties': forms.Textarea(attrs={'rows': 3}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'start_at': DATETIME_WIDGET,
            'end_at': DATETIME_WIDGET,
            'application_deadline': DATETIME_WIDGET,
        }


class CrewApplicationForm(StyledModelForm):
    availability_confirmed = forms.BooleanField(required=True)
    terms_acknowledged = forms.BooleanField(required=True)

    class Meta:
        model = CrewApplication
        fields = (
            'message', 'relevant_experience', 'proposed_amount', 'currency',
            'availability_confirmed', 'terms_acknowledged', 'needs_transport',
            'needs_accommodation',
        )
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'relevant_experience': forms.Textarea(attrs={'rows': 3}),
        }


class CrewApplicationReviewForm(StyledModelForm):
    class Meta:
        model = CrewApplication
        fields = ('status', 'internal_note', 'rejection_reason')
        widgets = {
            'internal_note': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }


class CrewOfferForm(StyledModelForm):
    class Meta:
        model = CrewOffer
        fields = (
            'compensation_type', 'amount', 'currency', 'bonus_amount',
            'expense_allowance', 'start_at', 'end_at', 'terms',
            'cancellation_terms', 'expires_at',
        )
        widgets = {
            'start_at': DATETIME_WIDGET,
            'end_at': DATETIME_WIDGET,
            'expires_at': DATETIME_WIDGET,
            'terms': forms.Textarea(attrs={'rows': 4}),
            'cancellation_terms': forms.Textarea(attrs={'rows': 3}),
        }


class CrewEngagementForm(StyledModelForm):
    class Meta:
        model = CrewEngagement
        fields = (
            'tour', 'crew', 'role', 'start_at', 'end_at', 'compensation_type',
            'agreed_amount', 'currency', 'bonus_amount', 'expense_allowance',
            'duties', 'schedule_note', 'meeting_point', 'cancellation_terms', 'status',
        )
        widgets = {
            'start_at': DATETIME_WIDGET, 'end_at': DATETIME_WIDGET,
            'duties': forms.Textarea(attrs={'rows': 3}),
            'schedule_note': forms.Textarea(attrs={'rows': 3}),
            'cancellation_terms': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crew'].queryset = CrewMember.objects.filter(
            verification_status='approved', available_for_work=True
        )


class CrewEngagementStatusForm(StyledModelForm):
    class Meta:
        model = CrewEngagement
        fields = ('status', 'schedule_note', 'meeting_point', 'cancellation_reason')
        widgets = {
            'schedule_note': forms.Textarea(attrs={'rows': 3}),
            'cancellation_reason': forms.Textarea(attrs={'rows': 3}),
        }


class CrewPaymentForm(StyledModelForm):
    class Meta:
        model = CrewPayment
        fields = (
            'base_amount', 'bonus_amount', 'approved_expenses', 'deductions',
            'currency', 'status', 'payment_method', 'payment_reference', 'receipt', 'note',
        )
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}

    def clean(self):
        cleaned = super().clean()
        values = [cleaned.get(name) or 0 for name in ('base_amount', 'bonus_amount', 'approved_expenses')]
        deductions = cleaned.get('deductions') or 0
        cleaned['net_amount'] = sum(values) - deductions
        if cleaned['net_amount'] < 0:
            self.add_error('deductions', 'Deductions cannot make the net payment negative.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.net_amount = instance.calculate_net()
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CrewReviewForm(StyledModelForm):
    class Meta:
        model = CrewReview
        fields = ('professionalism', 'knowledge', 'communication', 'punctuality', 'safety', 'overall', 'comment')
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}


class TrainingCourseForm(StyledModelForm):
    class Meta:
        model = TrainingCourse
        fields = (
            'title', 'code', 'description', 'content', 'required_for_roles',
            'passing_score', 'validity_months', 'is_active',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 6}),
            'required_for_roles': forms.CheckboxSelectMultiple(),
        }


class CrewTrainingRecordForm(StyledModelForm):
    class Meta:
        model = CrewTrainingRecord
        fields = ('crew', 'course', 'status', 'score', 'completed_at', 'expires_at', 'certificate')
        widgets = {'completed_at': DATETIME_WIDGET, 'expires_at': DATE_WIDGET}


class CrewCaseForm(StyledModelForm):
    class Meta:
        model = CrewCase
        fields = ('engagement', 'category', 'subject', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, crew=None, **kwargs):
        super().__init__(*args, **kwargs)
        if crew is not None:
            self.fields['engagement'].queryset = crew.engagements.all()


class CrewCaseResolutionForm(StyledModelForm):
    class Meta:
        model = CrewCase
        fields = ('status', 'assigned_to', 'resolution')
        widgets = {'resolution': forms.Textarea(attrs={'rows': 5})}


class SupplierProfileForm(StyledModelForm):
    class Meta:
        model = ServiceSupplier
        fields = (
            'legal_name', 'trading_name', 'entity_type', 'categories', 'contact_name',
            'phone', 'email', 'address', 'service_regions', 'business_license_number',
            'tax_number', 'contract_email', 'payout_method', 'payout_reference',
        )
        widgets = {'categories': forms.CheckboxSelectMultiple(), 'address': forms.Textarea(attrs={'rows': 3}), 'service_regions': forms.Textarea(attrs={'rows': 2})}


class SupplierOpsForm(SupplierProfileForm):
    class Meta(SupplierProfileForm.Meta):
        fields = SupplierProfileForm.Meta.fields + ('status', 'notes')
        widgets = dict(SupplierProfileForm.Meta.widgets, notes=forms.Textarea(attrs={'rows': 3}))


class SupplierDocumentForm(StyledModelForm):
    class Meta:
        model = SupplierDocument
        fields = ('document_type', 'title', 'file', 'reference_number', 'expires_at')
        widgets = {'expires_at': DATE_WIDGET}


class SupplierServiceForm(StyledModelForm):
    class Meta:
        model = SupplierService
        fields = ('category', 'name', 'description', 'unit', 'capacity', 'base_rate', 'currency', 'location', 'terms', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 3}), 'terms': forms.Textarea(attrs={'rows': 3})}


class SupplierAssetForm(StyledModelForm):
    class Meta:
        model = SupplierAsset
        fields = ('asset_type', 'name', 'reference', 'capacity', 'location', 'description', 'daily_rate', 'currency', 'document_expiry', 'is_available')
        widgets = {'description': forms.Textarea(attrs={'rows': 3}), 'document_expiry': DATE_WIDGET}


class SupplierContractForm(StyledModelForm):
    class Meta:
        model = SupplierContract
        fields = (
            'contract_number', 'title', 'start_date', 'end_date', 'currency',
            'value_ceiling', 'payment_terms', 'cancellation_terms', 'service_levels',
            'document', 'status',
        )
        widgets = {
            'start_date': DATE_WIDGET, 'end_date': DATE_WIDGET,
            'payment_terms': forms.Textarea(attrs={'rows': 3}),
            'cancellation_terms': forms.Textarea(attrs={'rows': 3}),
            'service_levels': forms.Textarea(attrs={'rows': 3}),
        }


class SupplierRateForm(StyledModelForm):
    class Meta:
        model = SupplierRate
        fields = ('service', 'description', 'unit', 'amount', 'currency', 'valid_from', 'valid_to', 'cancellation_deadline_hours')
        widgets = {'valid_from': DATE_WIDGET, 'valid_to': DATE_WIDGET}

    def __init__(self, *args, supplier=None, **kwargs):
        super().__init__(*args, **kwargs)
        if supplier is not None:
            self.fields['service'].queryset = supplier.services.all()


class ServiceRequirementForm(StyledModelForm):
    class Meta:
        model = ServiceRequirement
        fields = ('category', 'title', 'description', 'quantity', 'unit', 'start_at', 'end_at', 'location', 'budget_amount', 'currency', 'needed_by')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_at': DATETIME_WIDGET, 'end_at': DATETIME_WIDGET, 'needed_by': DATETIME_WIDGET,
        }


class RFQForm(StyledModelForm):
    class Meta:
        model = RequestForQuote
        fields = ('reference', 'instructions', 'deadline', 'status')
        widgets = {'instructions': forms.Textarea(attrs={'rows': 4}), 'deadline': DATETIME_WIDGET}


class SupplierQuoteForm(StyledModelForm):
    class Meta:
        model = SupplierQuote
        fields = ('amount', 'currency', 'details', 'cancellation_terms', 'valid_until', 'attachment')
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
            'cancellation_terms': forms.Textarea(attrs={'rows': 3}),
            'valid_until': DATETIME_WIDGET,
        }


class ServiceOrderForm(StyledModelForm):
    class Meta:
        model = ServiceOrder
        fields = (
            'supplier', 'contract', 'service', 'description', 'start_at', 'end_at',
            'quantity', 'unit', 'unit_price', 'total_amount', 'currency', 'status',
            'confirmation_reference', 'voucher', 'cancellation_terms', 'operational_note',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_at': DATETIME_WIDGET, 'end_at': DATETIME_WIDGET,
            'cancellation_terms': forms.Textarea(attrs={'rows': 3}),
            'operational_note': forms.Textarea(attrs={'rows': 3}),
        }


class ServiceOrderStatusForm(StyledModelForm):
    class Meta:
        model = ServiceOrder
        fields = ('status', 'confirmation_reference', 'voucher', 'operational_note')
        widgets = {'operational_note': forms.Textarea(attrs={'rows': 3})}


class SupplierInvoiceForm(StyledModelForm):
    class Meta:
        model = SupplierInvoice
        fields = ('invoice_number', 'amount', 'currency', 'issued_at', 'due_date', 'attachment', 'note')
        widgets = {'issued_at': DATE_WIDGET, 'due_date': DATE_WIDGET, 'note': forms.Textarea(attrs={'rows': 3})}


class SupplierInvoiceReviewForm(StyledModelForm):
    class Meta:
        model = SupplierInvoice
        fields = ('status', 'payment_reference', 'note')
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}


class SupplierReviewForm(StyledModelForm):
    class Meta:
        model = SupplierReview
        fields = ('quality', 'timeliness', 'contract_compliance', 'invoice_accuracy', 'overall', 'comment')
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}
