from django import forms
from .models import *
from datetime import date

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'adults', 'children', 'booking_date', 'notes']
        widgets = {
            'booking_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': date.today().isoformat()  # 🔒 This locks past dates
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'booking_date' and field.widget.__class__.__name__ != 'CheckboxInput':
                field.widget.attrs['class'] = 'form-control'

                

class EnquireUsForm(forms.ModelForm):
    class Meta:
        model = EnquireUs
        fields = ['full_name', 'email', 'phone', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super(EnquireUsForm, self).__init__(*args, **kwargs)

        placeholders = {
            'full_name': 'Enter your full name',
            'email': 'example@gmail.com',
            'phone': 'e.g. +93 700 000 000',
            'subject': 'Subject of your enquiry',
            'message': 'Write your message here...',
        }

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = placeholders.get(field_name, field.label)





from django import forms
from .models import Translator

class TranslatorForm(forms.ModelForm):
    class Meta:
        model = Translator
        fields = [
            'name',
            'gender',
            'date_of_birth',
            'phone',
            'email',
            'languages',
            'experience_years',
            'certifications',
            'bio',
            'profile_image',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter full name',
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter phone number',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter email address',
        })
        self.fields['languages'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g. English ↔ Pashto, Chinese ↔ Dari',
        })
        self.fields['experience_years'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Years of experience',
            'min': 0,
            'type': 'number',
        })
        self.fields['certifications'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter certifications or qualifications',
        })
        self.fields['bio'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Short biography',
        })
        self.fields['profile_image'].widget.attrs.update({
            'class': 'form-control',
        })




class TourGuideForm(forms.ModelForm):
    class Meta:
        model = TourGuide
        fields = [
            'name', 'gender', 'phone', 'email', 'provinces', 'languages', 'experience_years',
            'specialties', 'bio', 'id_number', 'certifications', 'cv', 'profile_image'
        ]
        widgets = {
            'specialties': forms.CheckboxSelectMultiple(),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
        }

        



class PreArrivalRequirementForm(forms.ModelForm):
    class Meta:
        model = PreArrivalRequirement
        fields = [
            'visa_status', 'visa_copy', 'passport_copy',
            'travel_start_date', 'travel_end_date', 'embassy_location',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_email',
            'has_medical_conditions', 'medical_notes','safety_guideline_accepted'
        ]
        widgets = {
            'travel_start_date': forms.DateInput(attrs={'type': 'date'}),
            'travel_end_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'visa_status': 'Have you received your Afghan visa?',
            'visa_copy': 'Upload visa copy',
            'passport_copy': 'Upload your passport',
            'embassy_location': 'Embassy/Consulate for visa application',
            'safety_guideline_accepted': 'I have read and accepted the safety guidelines',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap classes
        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs.setdefault('class', 'form-check-input')
            else:
                f.widget.attrs.setdefault('class', 'form-control')

        # Make all fields optional here; we’ll enforce conditional requirements in clean()
        for name, f in self.fields.items():
            if name != 'visa_status':
                f.required = False

        # Ensure predictable id for JS
        self.fields['visa_status'].widget.attrs['id'] = 'id_visa_status'

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get('visa_status')
        errors = {}

        if status == 'yes':
            # Only visa_copy required
            if not cleaned.get('visa_copy'):
                errors['visa_copy'] = 'Please upload your visa copy.'
        elif status == 'no':
            # All others required (except visa_copy)
            required_when_no = [
                'passport_copy', 'travel_start_date', 'travel_end_date', 'embassy_location',
                'emergency_contact_name', 'emergency_contact_phone', 'safety_guideline_accepted'
            ]
            for f in required_when_no:
                v = cleaned.get(f)
                # safety_guideline_accepted is boolean; must be True
                if f == 'safety_guideline_accepted':
                    if v is not True:
                        errors[f] = 'You must accept the safety guidelines.'
                else:
                    if not v:
                        errors[f] = 'This field is required.'
        else:
            errors['visa_status'] = 'Please select your visa status.'

        if errors:
            raise forms.ValidationError(errors)
        return cleaned



class PreArrivalForm(forms.ModelForm):
    class Meta:
        model = PreArrival
        fields = [
            'passport_copy', 'visa_copy',
            'flight_ticket', 'flight_date', 'flight_time',
            'airline_name', 'flight_number',
            'entry_point', 'entry_point_other',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_email',
            'has_medical_conditions', 'medical_details',
            'safety_acknowledgement',
            'additional_notes',
        ]
        widgets = {
            'flight_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'flight_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'medical_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'passport_copy': 'Passport Copy (required)',
            'visa_copy': 'Visa Copy (if available)',
            'flight_ticket': 'Flight Ticket / Reservation (required)',
            'entry_point': 'Entry Point to Afghanistan',
            'entry_point_other': "If 'Other', please specify",
            'safety_acknowledgement': 'I have read and accept the safety guidelines',
        }

    def clean(self):
        cleaned = super().clean()
        entry_point = cleaned.get('entry_point')
        entry_point_other = cleaned.get('entry_point_other')
        safety_ack = cleaned.get('safety_acknowledgement')

        # If "Other", require the text input
        if entry_point == 'other' and not entry_point_other:
            self.add_error('entry_point_other', "Please specify your entry point.")

        # Must tick safety checkbox
        if not safety_ack:
            self.add_error('safety_acknowledgement', "You must accept the safety guidelines.")

        return cleaned
    



class PickupPlanForm(forms.ModelForm):
    class Meta:
        model = PickupPlan
        fields = [
            'pickup_type','entry_point_label','entry_point_code',
            'scheduled_at','window_minutes',
            'driver','operator','vehicle',
            'driver_phone_share','operator_phone_share','tourist_phone_share',
            'meeting_point','meeting_note','welcome_note',
            'visible_to_tourist','otp_code','checkin_photo',
        ]
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'meeting_note': forms.Textarea(attrs={'rows':3, 'class':'form-control'}),
            'welcome_note': forms.TextInput(attrs={'class':'form-control'}),
        }