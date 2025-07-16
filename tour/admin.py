from django.contrib import admin
from .models import *

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1




@admin.register(TourCategory)
class TourCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Booking)

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


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location', 'available', 'get_assigned_guide')
    list_filter = ( 'available', 'start_date')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TourGuideInterestInline]

    def get_assigned_guide(self, obj):
        try:
            return obj.assigned_guide
        except TourGuideAssignment.DoesNotExist:
            return "—"
    get_assigned_guide.short_description = 'Assigned Guide'


# @admin.register(TourGuideInterest)
# class TourGuideInterestAdmin(admin.ModelAdmin):
#     list_display = ('tour', 'guide', 'applied_at', 'is_shortlisted', 'is_selected')
#     list_filter = ('is_shortlisted', 'is_selected', 'applied_at')
#     search_fields = ('guide__username', 'tour__title')
#     autocomplete_fields = ('tour', 'guide')


@admin.register(TourGuideAssignment)
class TourGuideAssignmentAdmin(admin.ModelAdmin):
    list_display = ('tour', 'assigned_at', 'bonus_amount')
    search_fields = ('guide__username', 'tour__title')
    autocomplete_fields = ('tour',)


admin.site.register(ItineraryItem)
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

admin.site.register(Languages)
admin.site.register(Translator)
admin.site.register(SecurityGuard)