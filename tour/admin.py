from django.contrib import admin
from .models import *
from django import forms



class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1


@admin.register(TourCategory)
class TourCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EnquireUs)
class EnquireUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'tour', 'date_created', 'responded')
    search_fields = ('full_name', 'email', 'subject')
    list_filter = ('responded', 'date_created')
# admin.py

from .models import ItineraryItem

class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    extra = 1

class TourGuideInterestInline(admin.TabularInline):
    model = TourGuideInterest
    extra = 0
    fields = ('guide', 'applied_at', 'is_shortlisted', 'is_selected', 'message')
    readonly_fields = ('applied_at',)
    show_change_link = True


# Custom form for injecting JS
class TourAdminForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'

    class Media:
        js = ('admin/js/tour_form.js',)  # Make sure this path is correct

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    form = TourAdminForm
    list_display = ('title', 'start_date', 'location', 'available', 'get_assigned_guide')
    list_filter = ('available', 'start_date')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TourGuideInterestInline, TourImageInline]

    def get_assigned_guide(self, obj):
        try:
            return obj.assigned_guide
        except TourGuideAssignment.DoesNotExist:
            return "—"
    get_assigned_guide.short_description = 'Assigned Guide'


@admin.register(TourGuideAssignment)
class TourGuideAssignmentAdmin(admin.ModelAdmin):
    list_display = ('tour', 'assigned_at', 'bonus_amount')
    search_fields = ('guide__username', 'tour__title')
    autocomplete_fields = ('tour',)


class ItineraryItemForm(forms.ModelForm):
    class Meta:
        model = ItineraryItem
        fields = '__all__'

    class Media:
        js = ('admin/js/itinerary_filter.js',)  # We'll write this JS file next

@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    form = ItineraryItemForm

    
admin.site.register(Frequently_asked_questions)
admin.site.register(User_favorite_tour)
admin.site.register(Ready_tour_for_booking)


class AccommodationImageInline(admin.TabularInline):  # or use StackedInline
    model = AccommodationImage
    extra = 1  # Number of empty forms to show

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'location', 'price_per_night']
    inlines = [AccommodationImageInline]

class TransportImageInline(admin.TabularInline):
    model = TransportImage
    extra = 1

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ['type', 'departure_location', 'arrival_location', 'departure_time', 'price']
    inlines = [TransportImageInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # REQUIRED for other admins' autocomplete_fields
    search_fields = (
        "id",
        "tour__title",
        "user__username", "user__first_name", "user__last_name",
        "email", "phone",
    )
    list_display = ("id", "tour", "user", "booking_date", "situation", "paid")
    raw_id_fields = ("tour", "user")   # optional nicety

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    search_fields = ("name", "phone", "languages")

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    search_fields = ("name", "phone", "languages")

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    search_fields = ("title", "plate_no", "color")

@admin.register(PreArrival)
class PreArrivalAdmin(admin.ModelAdmin):
    # You can keep your existing config — but E040 is about the related admins above.
    search_fields = (
        "booking__id", "booking__tour__title",
        "user__username", "user__first_name", "user__last_name",
        "airline_name", "flight_number", "entry_point_other",
        "emergency_contact_name", "emergency_contact_phone",
    )
    raw_id_fields = ("user", "booking")
    # ...rest unchanged...

@admin.register(PickupPlan)
class PickupPlanAdmin(admin.ModelAdmin):
    search_fields = (
        "booking__id", "booking__tour__title",
        "entry_point_label",
        "driver__name", "operator__name",
        "vehicle__title", "vehicle__plate_no",
    )
    autocomplete_fields = ("booking", "driver", "operator", "vehicle")
    # ...rest unchanged...

@admin.register(GiftItem)
class GiftItemAdmin(admin.ModelAdmin):
    list_display = ("name", "is_afghan_special")
    search_fields = ("name",)
    list_filter = ("is_afghan_special",)


@admin.register(WelcomePackage)
class WelcomePackageAdmin(admin.ModelAdmin):
    list_display = ("booking", "user", "prepared_at", "delivered_at")
    search_fields = ("booking__id", "user__username", "user__first_name", "user__last_name")
    raw_id_fields = ("booking", "user", "gifts")    




admin.site.register(Languages)
admin.site.register(Translator)
admin.site.register(SecurityGuard)










