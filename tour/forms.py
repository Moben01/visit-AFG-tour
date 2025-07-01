from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'persons', 'booking_date', 'notes']


from django.forms import modelformset_factory
from .models import ItineraryItem

ItineraryFormSet = modelformset_factory(
    ItineraryItem,
    fields=('day_number', 'title', 'description', 'time'),
    extra=1,
    can_delete=True
)















