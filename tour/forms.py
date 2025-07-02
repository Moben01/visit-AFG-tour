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