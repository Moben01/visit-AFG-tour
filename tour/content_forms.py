from datetime import datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from home.models import (
    ContentItem,
    ContentSection,
    ManagedMedia,
    PopularPlace,
    ProvincePage,
    ProvincePageSection,
    TourHomepageFeature,
)
from things_to_do.models import (
    Best_Selling,
    Best_places_for_visit,
    Popular_Tourist,
    Top_things_to_do_in_province,
)

from .models import ItineraryItem, Tour, TourCategory


class ContentModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "ops-input")
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 5)


class PopularPlaceContentForm(ContentModelForm):
    class Meta:
        model = PopularPlace
        fields = (
            "title",
            "province",
            "description",
            "preview_image",
            "static_image",
            "province_page",
            "url_name",
            "external_url",
            "display_order",
            "is_active",
        )


class ContentSectionForm(ContentModelForm):
    class Meta:
        model = ContentSection
        fields = (
            "key",
            "name",
            "eyebrow",
            "title",
            "body",
            "button_label",
            "button_url_name",
            "button_external_url",
            "image",
            "static_image",
            "display_order",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["key"].disabled = True

    def clean_button_url_name(self):
        value = self.cleaned_data.get("button_url_name", "").strip()
        if value:
            try:
                reverse(value)
            except NoReverseMatch as exc:
                raise forms.ValidationError("This Django URL name could not be resolved.") from exc
        return value


class ContentItemForm(ContentModelForm):
    class Meta:
        model = ContentItem
        fields = (
            "section",
            "title",
            "subtitle",
            "body",
            "icon_class",
            "image",
            "static_image",
            "link_label",
            "url_name",
            "external_url",
            "display_order",
            "is_active",
        )

    def clean_url_name(self):
        value = self.cleaned_data.get("url_name", "").strip()
        if value:
            try:
                reverse(value)
            except NoReverseMatch as exc:
                raise forms.ValidationError("This Django URL name could not be resolved.") from exc
        return value


class ProvincePageForm(ContentModelForm):
    class Meta:
        model = ProvincePage
        fields = (
            "name",
            "slug",
            "summary",
            "body",
            "hero_image",
            "static_hero_image",
            "meta_title",
            "meta_description",
            "is_published",
        )


class ProvincePageSectionForm(ContentModelForm):
    class Meta:
        model = ProvincePageSection
        fields = (
            "page",
            "heading",
            "body",
            "image",
            "static_image",
            "display_order",
            "is_active",
        )


class ManagedMediaForm(ContentModelForm):
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024
    ALLOWED_EXTENSIONS = {
        "image": {".jpg", ".jpeg", ".png", ".webp", ".gif"},
        "document": {".pdf", ".doc", ".docx", ".xls", ".xlsx"},
        "video": {".mp4", ".webm", ".mov"},
        "other": {".txt", ".csv", ".zip"},
    }

    class Meta:
        model = ManagedMedia
        fields = ("title", "file", "alt_text", "category", "is_active")

    def clean_file(self):
        uploaded = self.cleaned_data.get("file")
        if not uploaded:
            return uploaded
        if uploaded.size > self.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Files may not exceed 20 MB.")
        category = self.data.get("category") or self.instance.category or "image"
        extension = Path(uploaded.name).suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS.get(category, set()):
            raise forms.ValidationError("This file type is not allowed for the selected category.")
        return uploaded


class TourCategoryContentForm(ContentModelForm):
    class Meta:
        model = TourCategory
        fields = ("name", "slug", "icon", "description")


class TourWebsiteContentForm(ContentModelForm):
    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    price_on_request = forms.BooleanField(
        required=False,
        label=_("Price on request"),
        help_text=_("Show an enquiry action instead of accepting an online booking."),
    )
    google_location = forms.URLField(
        required=False,
        label=_("Google Maps embed URL"),
        help_text=_("Optional. Paste the HTTPS URL used by the public map embed."),
        widget=forms.URLInput(attrs={"placeholder": "https://www.google.com/maps/embed?..."}),
    )
    homepage_featured = forms.BooleanField(
        required=False,
        label=_("Feature on homepage"),
        help_text=_("Only published tours with complete homepage metadata are displayed."),
    )
    homepage_physical_level = forms.ChoiceField(
        required=False,
        choices=(("", _("Choose a physical level")),) + TourHomepageFeature.PHYSICAL_LEVEL_CHOICES,
        label=_("Physical level"),
    )
    homepage_display_order = forms.IntegerField(
        required=False,
        min_value=0,
        initial=0,
        label=_("Homepage display order"),
    )

    class Meta:
        model = Tour
        fields = (
            "category",
            "title",
            "type",
            "description",
            "start_date",
            "end_date",
            "duration_day",
            "duration_night",
            "location",
            "price",
            "price_on_request",
            "image",
            "google_location",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": _("Describe the experience, pace and main highlights."),
                }
            ),
            "duration_day": forms.NumberInput(attrs={"min": 1, "step": 1}),
            "duration_night": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "location": forms.CheckboxSelectMultiple(),
            "price": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "image": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }
        labels = {
            "category": _("Category"),
            "title": _("Tour title"),
            "type": _("Booking type"),
            "description": _("Tour description"),
            "start_date": _("Start date"),
            "end_date": _("End date"),
            "duration_day": _("Number of days"),
            "duration_night": _("Number of nights"),
            "location": _("Destinations"),
            "price": _("Price per traveller (USD)"),
            "image": _("Cover image"),
        }
        help_texts = {
            "title": _("The slug is generated automatically from this title."),
            "type": _("Scheduled tours use fixed dates; on-request tours do not."),
            "duration_day": _("Must match the number of itinerary days before publishing."),
            "image": _("JPG, PNG or WebP, up to 10 MB. Required only when publishing."),
        }

    def __init__(self, *args, publish=False, **kwargs):
        self.publish = publish
        super().__init__(*args, **kwargs)
        optional_fields = (
            "start_date",
            "end_date",
            "duration_day",
            "duration_night",
            "location",
            "price",
            "image",
            "google_location",
        )
        for field_name in optional_fields:
            self.fields[field_name].required = False

        self.fields["type"].choices = (
            ("", _("Choose a booking type")),
            ("schedule", _("Scheduled tour")),
            ("not_schedule", _("On request / flexible dates")),
        )
        self.fields["title"].widget.attrs.setdefault("placeholder", _("e.g. Bamyan cultural journey"))
        self.fields["location"].widget.attrs["class"] = "ops-province-options"
        self.fields["price_on_request"].widget.attrs["data-price-on-request"] = ""
        self.fields["price"].widget.attrs["data-tour-price"] = ""
        if self.instance and self.instance.pk and self.instance.is_price_on_request:
            self.initial["price_on_request"] = True
        if self.instance and self.instance.pk:
            feature = getattr(self.instance, "homepage_feature", None)
            if feature:
                self.initial["homepage_featured"] = feature.is_active
                self.initial["homepage_physical_level"] = feature.physical_level
                self.initial["homepage_display_order"] = feature.display_order

    def clean_image(self):
        uploaded = self.cleaned_data.get("image")
        if not isinstance(uploaded, UploadedFile):
            return uploaded
        if uploaded.size > self.MAX_IMAGE_SIZE:
            raise forms.ValidationError(_("The cover image may not exceed 10 MB."))
        if Path(uploaded.name).suffix.lower() not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise forms.ValidationError(_("Use a JPG, PNG or WebP cover image."))
        return uploaded

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        tour_type = cleaned.get("type")
        duration_day = cleaned.get("duration_day")
        duration_night = cleaned.get("duration_night")

        if tour_type != "schedule":
            cleaned["start_date"] = None
            cleaned["end_date"] = None
            start = end = None
        if start and end and end < start:
            self.add_error("end_date", _("End date cannot be before start date."))

        for field_name, value, minimum in (
            ("duration_day", duration_day, 1),
            ("duration_night", duration_night, 0),
        ):
            if value in (None, ""):
                cleaned[field_name] = ""
                continue
            try:
                number = int(value)
            except (TypeError, ValueError):
                self.add_error(field_name, _("Enter a whole number."))
                continue
            if number < minimum:
                self.add_error(
                    field_name,
                    _("Enter %(minimum)s or more.") % {"minimum": minimum},
                )
            cleaned[field_name] = str(number)

        if cleaned.get("price_on_request"):
            cleaned["price"] = Decimal("0.00")
        elif cleaned.get("price") is None:
            cleaned["price"] = Decimal("0.00")

        if self.publish:
            if tour_type == "schedule":
                if not start:
                    self.add_error("start_date", _("A scheduled tour needs a start date."))
                if not end:
                    self.add_error("end_date", _("A scheduled tour needs an end date."))
            if not duration_day:
                self.add_error("duration_day", _("Add the tour duration before publishing."))
            if not cleaned.get("location"):
                self.add_error("location", _("Select at least one destination before publishing."))
            if not cleaned.get("price_on_request") and cleaned.get("price", 0) <= 0:
                self.add_error("price", _("Enter a price or select Price on request."))
            current_image = self.instance.image if self.instance and self.instance.pk else None
            if not (cleaned.get("image") or current_image):
                self.add_error("image", _("Add a cover image before publishing."))

            itinerary_count = self.instance.itinerary_items.count() if self.instance.pk else 0
            if not itinerary_count:
                self.add_error(None, _("Add at least one itinerary day before publishing."))
            elif duration_day:
                try:
                    if itinerary_count != int(duration_day):
                        self.add_error(
                            "duration_day",
                            _("Duration must match the %(count)s itinerary days.")
                            % {"count": itinerary_count},
                        )
                except (TypeError, ValueError):
                    pass
        if cleaned.get("homepage_featured") and not cleaned.get("homepage_physical_level"):
            self.add_error(
                "homepage_physical_level",
                _("Select a physical level before featuring this tour."),
            )
        return cleaned

    def save_homepage_feature(self, tour):
        is_active = bool(self.cleaned_data.get("homepage_featured"))
        feature = getattr(tour, "homepage_feature", None)
        if not is_active and feature is None:
            return None
        values = {
            "is_active": is_active,
            "display_order": self.cleaned_data.get("homepage_display_order") or 0,
        }
        physical_level = self.cleaned_data.get("homepage_physical_level")
        if physical_level:
            values["physical_level"] = physical_level
        elif feature:
            values["physical_level"] = feature.physical_level
        feature, _created = TourHomepageFeature.objects.update_or_create(
            tour=tour,
            defaults=values,
        )
        return feature


class ItineraryItemContentForm(ContentModelForm):
    MAX_IMAGE_SIZE = TourWebsiteContentForm.MAX_IMAGE_SIZE
    ALLOWED_IMAGE_EXTENSIONS = TourWebsiteContentForm.ALLOWED_IMAGE_EXTENSIONS

    date = forms.DateField(
        required=False,
        label=_("Date"),
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text=_("Optional. It is calculated from the tour start date when left empty."),
    )

    class Meta:
        model = ItineraryItem
        fields = (
            "title",
            "description",
            "date",
            "image",
            "type_of_transport",
            "transport",
            "accommodation",
            "meals",
            "logistics",
            "tour_guide",
        )
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 6, "placeholder": _("Describe the route, activities and overnight plan.")}
            ),
            "image": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }
        labels = {
            "title": _("Day title"),
            "description": _("Day description"),
            "image": _("Day image"),
            "type_of_transport": _("Transport mode"),
            "transport": _("Transport record"),
            "accommodation": _("Accommodation"),
            "meals": _("Meal plan"),
            "logistics": _("Logistics"),
            "tour_guide": _("Tour guide"),
        }
        help_texts = {
            "image": _("Optional JPG, PNG or WebP, up to 10 MB."),
            "transport": _("Optional. Select a detailed transport record if one exists."),
        }

    def __init__(self, *args, tour, **kwargs):
        self.tour = tour
        super().__init__(*args, **kwargs)
        for field_name in ("title", "date", "image", "type_of_transport"):
            self.fields[field_name].required = False
        self.fields["type_of_transport"].choices = (
            ("", _("No transport specified")),
            *ItineraryItem.TRANSPORT_TYPE,
        )
        if self.instance and self.instance.pk and self.instance.date:
            self.initial["date"] = timezone.localtime(self.instance.date).date()

    def clean_image(self):
        uploaded = self.cleaned_data.get("image")
        if not isinstance(uploaded, UploadedFile):
            return uploaded
        if uploaded.size > self.MAX_IMAGE_SIZE:
            raise forms.ValidationError(_("The day image may not exceed 10 MB."))
        if Path(uploaded.name).suffix.lower() not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise forms.ValidationError(_("Use a JPG, PNG or WebP day image."))
        return uploaded

    def clean_date(self):
        selected_date = self.cleaned_data.get("date")
        if (
            selected_date
            and self.tour.type == "schedule"
            and self.tour.start_date
            and selected_date < self.tour.start_date
        ):
            raise forms.ValidationError(_("The itinerary date cannot be before the tour start date."))
        if (
            selected_date
            and self.tour.type == "schedule"
            and self.tour.end_date
            and selected_date > self.tour.end_date
        ):
            raise forms.ValidationError(_("The itinerary date cannot be after the tour end date."))
        return selected_date

    def save_for_tour(self, day_number):
        item = super().save(commit=False)
        item.tour = self.tour
        item.day_number = day_number
        selected_date = self.cleaned_data.get("date")
        if not selected_date:
            base_date = self.tour.start_date or timezone.localdate()
            selected_date = base_date + timedelta(days=max(day_number - 1, 0))
        item.date = timezone.make_aware(
            datetime.combine(selected_date, time.min),
            timezone.get_current_timezone(),
        )
        item.save()
        return item


class BestPlaceContentForm(ContentModelForm):
    class Meta:
        model = Best_places_for_visit
        fields = ("title", "image", "description", "location", "provinces")


class TopThingContentForm(ContentModelForm):
    class Meta:
        model = Top_things_to_do_in_province
        fields = ("title", "image", "description", "location", "price", "provinces")


class TouristAttractionContentForm(ContentModelForm):
    class Meta:
        model = Popular_Tourist
        fields = ("title", "image", "description", "location", "provinces")


class BestSellingContentForm(ContentModelForm):
    class Meta:
        model = Best_Selling
        fields = ("title", "image", "description", "location", "provinces")
