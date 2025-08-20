from django.contrib import admin
from .models import *

# Inline for adding images directly on the place page
class BestPlacesForVisitImagesInline(admin.TabularInline):  # or StackedInline
    model = Best_places_for_visit_images
    extra = 1  # how many empty image forms to show by default

@admin.register(Best_places_for_visit)
class BestPlacesForVisitAdmin(admin.ModelAdmin):
    list_display = ('title', 'location')
    search_fields = ('title', 'location')
    list_filter = ('provinces',)
    inlines = [BestPlacesForVisitImagesInline]  # add images inside the form

# Optional: You can still register the image model separately if needed
@admin.register(Best_places_for_visit_images)
class BestPlacesForVisitImagesAdmin(admin.ModelAdmin):
    list_display = ('caption', 'get_place_title')

    def get_place_title(self, obj):
        return obj.place.title

    get_place_title.short_description = 'Place'


# Things to do 

# Inline for adding images directly on the place page
class Top_things_to_do_in_province_imagesInline(admin.TabularInline):  # or StackedInline
    model = Top_things_to_do_in_province_images
    extra = 1  # how many empty image forms to show by default


@admin.register(Top_things_to_do_in_province)
class TopThingsToDoInProvinceAdmin(admin.ModelAdmin):
    list_display = ('title', 'location')
    search_fields = ('title', 'location')
    list_filter = ('provinces',)
    inlines = [Top_things_to_do_in_province_imagesInline]  # add images inside the form


@admin.register(Top_things_to_do_in_province_images)
class TopThingsToDoInProvinceImagesAdmin(admin.ModelAdmin):
    list_display = ('caption', 'get_place_title')

    def get_place_title(self, obj):
        return obj.place.title

    get_place_title.short_description = 'Place'
