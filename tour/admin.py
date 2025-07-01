from django.contrib import admin
from .models import *

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TourImageInline]
    list_display = ('title', 'location', 'available', 'price')

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

admin.site.register(ItineraryItem)
admin.site.register(Frequently_asked_questions)