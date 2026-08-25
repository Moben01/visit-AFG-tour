from django import forms

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

