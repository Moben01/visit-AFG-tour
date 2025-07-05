from django import forms
from .models import *

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'persons', 'booking_date', 'notes']


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