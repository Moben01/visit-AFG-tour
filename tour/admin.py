from django.contrib import admin
from .models import Frequently_asked_questions, TourCategory, Tour, TourImage, Booking

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

# admin.py

from .models import ItineraryItem

class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    extra = 1

admin.site.register(ItineraryItem)
admin.site.register(Frequently_asked_questions)