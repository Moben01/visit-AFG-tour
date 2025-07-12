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