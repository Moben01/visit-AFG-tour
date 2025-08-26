from django.contrib import admin
from .models import *
from django.contrib import admin
from .models import Best_Selling, Best_Selling_images






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





from django.contrib import admin
from .models import Popular_Tourist, Popular_Tourist_images


# Inline for adding images directly on the place page
class PopularTouristImagesInline(admin.TabularInline):  # or admin.StackedInline
    model = Popular_Tourist_images
    extra = 1  # how many empty image forms to show by default


@admin.register(Popular_Tourist)
class PopularTouristAdmin(admin.ModelAdmin):
    list_display = ('title', 'location')
    search_fields = ('title', 'location')
    list_filter = ('provinces',)
    inlines = [PopularTouristImagesInline]  # add images inside the form


# Optional: register image model separately if you want
@admin.register(Popular_Tourist_images)
class PopularTouristImagesAdmin(admin.ModelAdmin):
    list_display = ('caption', 'get_place_title')

    def get_place_title(self, obj):
        return obj.place.title

    get_place_title.short_description = 'Place'





# Inline برای افزودن تصاویر داخل صفحه Best_Selling
class BestSellingImagesInline(admin.TabularInline):  # یا StackedInline
    model = Best_Selling_images
    extra = 1  # تعداد فرم‌های خالی برای تصویر جدید

@admin.register(Best_Selling)
class BestSellingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location')
    search_fields = ('title', 'location')
    list_filter = ('provinces',)
    inlines = [BestSellingImagesInline]

# ثبت جداگانه مدل تصاویر (اختیاری)
@admin.register(Best_Selling_images)
class BestSellingImagesAdmin(admin.ModelAdmin):
    list_display = ('caption', 'get_province_title')

    def get_province_title(self, obj):
        return obj.province.title  # توجه: فیلد ForeignKey شما province است
    get_province_title.short_description = 'Place'
