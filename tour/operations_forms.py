from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from django.db.models import Q

from home.models import (
    EntryPlan,
    RouteProposal,
    RouteProposalDay,
    TripRequest,
)
from .models import Booking, PickupPlan, Tour, WelcomePackage


class BookingOperationsForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            'name', 'email', 'phone', 'booking_date',
            'adults', 'children', 'notes',
        )
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')


class BookingStatusForm(forms.Form):
    situation = forms.ChoiceField(choices=Booking.BOOKING_SIT)
    reason = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Required for cancellations and reopening a booking.',
        required=False,
    )

    def __init__(self, *args, allowed_statuses=None, **kwargs):
        super().__init__(*args, **kwargs)
        if allowed_statuses is not None:
            labels = dict(Booking.BOOKING_SIT)
            self.fields['situation'].choices = [
                (value, labels[value]) for value in allowed_statuses
            ]
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('situation') == 'Cancelled' and not cleaned.get('reason', '').strip():
            self.add_error('reason', 'A cancellation reason is required.')
        return cleaned


class ManualPaymentForm(forms.Form):
    amount = forms.IntegerField(min_value=0)
    reference = forms.CharField(max_length=120)
    reason = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')


class TourOperationsForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = (
            'start_date', 'end_date', 'available',
            'tour_guide', 'translator', 'security_gard',
        )
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'End date cannot be before start date.')
        return cleaned


class PickupPlanOperationsForm(forms.ModelForm):
    class Meta:
        model = PickupPlan
        fields = (
            'pickup_type', 'entry_point_label', 'entry_point_code',
            'scheduled_at', 'window_minutes', 'driver', 'operator', 'vehicle',
            'driver_phone_share', 'operator_phone_share', 'tourist_phone_share',
            'meeting_point', 'meeting_note', 'welcome_note',
            'visible_to_tourist', 'status', 'otp_code', 'checkin_photo',
            'no_show_reason',
        )
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'meeting_note': forms.Textarea(attrs={'rows': 3}),
            'no_show_reason': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('status') == 'no_show' and not cleaned.get('no_show_reason', '').strip():
            self.add_error('no_show_reason', 'A no-show reason is required.')
        return cleaned


class WelcomePackageOperationsForm(forms.ModelForm):
    class Meta:
        model = WelcomePackage
        fields = (
            'welcome_letter', 'sim_card', 'printed_itinerary',
            'local_map', 'emergency_numbers_card', 'gifts',
            'package_photo', 'special_notes', 'prepared_at', 'delivered_at',
        )
        widgets = {
            'prepared_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'delivered_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'special_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')


class TripRequestOperationsForm(forms.ModelForm):
    assigned_expert = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label='Assigned expert',
    )

    class Meta:
        model = TripRequest
        fields = (
            'status', 'full_name', 'email', 'phone', 'start_date', 'end_date',
            'adults', 'children', 'budget_tier', 'estimated_budget', 'pace', 'notes',
        )
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields['assigned_expert'].queryset = User.objects.filter(
            Q(is_staff=True)
            | Q(is_superuser=True)
            | Q(my_choice_field__in=('Guide', 'Operator', 'Moderator'))
        ).order_by('first_name', 'last_name', 'username')
        if self.instance and self.instance.assigned_expert_id:
            self.fields['assigned_expert'].initial = self.instance.assigned_expert_id
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'End date cannot be before start date.')
        if cleaned.get('status') == 'booked' and not self.instance.booking_id:
            self.add_error('status', 'Use Convert to booking so the route remains linked to a real booking.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        expert = self.cleaned_data.get('assigned_expert')
        instance.assigned_expert_id = expert.pk if expert else None
        if commit:
            instance.save()
        return instance


class EntryPlanOperationsForm(forms.ModelForm):
    class Meta:
        model = EntryPlan
        fields = (
            'selection_mode', 'transport_mode', 'arrival_origin',
            'selected_entry_point', 'other_entry_point',
            'recommended_entry_point', 'alternatives', 'operator_notes', 'status',
        )
        widgets = {
            'alternatives': forms.Textarea(attrs={'rows': 3}),
            'operator_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('status') in {'recommended', 'confirmed'} and not (
            cleaned.get('recommended_entry_point')
            or cleaned.get('selected_entry_point')
        ):
            self.add_error('recommended_entry_point', 'Prepare an entry recommendation before advancing its status.')
        return cleaned


class RouteProposalOperationsForm(forms.ModelForm):
    booking_tour = forms.ModelChoiceField(
        queryset=Tour.objects.none(),
        required=False,
        help_text='Required only when converting an accepted proposal into a payable booking.',
    )

    class Meta:
        model = RouteProposal
        fields = (
            'title', 'summary', 'proposed_entry_point', 'total_price',
            'currency', 'valid_until', 'customer_message', 'internal_notes',
        )
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 5}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'customer_message': forms.Textarea(attrs={'rows': 4}),
            'internal_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking_tour'].queryset = Tour.objects.filter(available=True).order_by('title')
        if self.instance and self.instance.booking_tour_id:
            self.fields['booking_tour'].initial = self.instance.booking_tour_id
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')

    def save(self, commit=True):
        instance = super().save(commit=False)
        tour = self.cleaned_data.get('booking_tour')
        instance.booking_tour_id = tour.pk if tour else None
        if commit:
            instance.save()
        return instance


class RouteProposalDayOperationsForm(forms.ModelForm):
    class Meta:
        model = RouteProposalDay
        fields = (
            'day_number', 'destination', 'title', 'description',
            'transport', 'overnight_location',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ops-input')


RouteProposalDayFormSet = inlineformset_factory(
    RouteProposal,
    RouteProposalDay,
    form=RouteProposalDayOperationsForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

