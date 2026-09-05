import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .validators import (
    PLACEHOLDER_DOMAINS,
    validate_brand_asset_size,
    validate_domain_name,
    validate_licence_number,
    validate_phone_number,
)


__all__ = [
    "Main_things",
    "TourHomepageFeature",
    "ContentSection",
    "ContentItem",
    "ProvincePage",
    "ProvincePageSection",
    "ManagedMedia",
    "PopularPlace",
    "PlaceImage",
    "TripRequest",
    "TripStop",
    "TripPreference",
    "EntryPlan",
    "RouteProposal",
    "RouteProposalDay",
]


def _resolved_url(url_name, external_url):
    if external_url:
        return external_url
    if not url_name:
        return ""
    try:
        return reverse(url_name)
    except NoReverseMatch:
        return ""


def _resolved_image(uploaded_image, static_image):
    if uploaded_image:
        try:
            return uploaded_image.url
        except ValueError:
            pass
    return static(static_image) if static_image else ""


def default_public_languages():
    return ["en", "fa", "ar"]


HOSTING_SERVICE_GROUPS = (
    (
        "before_arrival",
        _("Before arrival"),
        (
            ("trip_consultation", _("Trip consultation")),
            ("itinerary", _("Itinerary")),
            ("visa_guidance", _("Visa guidance")),
            ("preparation_checklist", _("Preparation checklist")),
            ("cultural_guidance", _("Cultural guidance")),
            ("payment_arrival_information", _("Payment and arrival information")),
        ),
    ),
    (
        "on_arrival",
        _("On arrival"),
        (
            ("airport_welcome", _("Airport welcome when included")),
            ("arrival_transfer", _("Transfer")),
            ("guide_introduction", _("Guide introduction")),
            ("itinerary_briefing", _("Itinerary briefing")),
        ),
    ),
    (
        "during_journey",
        _("During the journey"),
        (
            ("local_guide", _("Local guide")),
            ("coordinated_vehicle", _("Coordinated vehicle")),
            ("accommodation_coordination", _("Accommodation coordination")),
            ("route_review", _("Route review")),
            ("operations_contact", _("Operations contact")),
            ("documented_changes", _("Documented changes")),
        ),
    ),
    (
        "before_departure",
        _("Before departure"),
        (
            ("departure_transfer", _("Airport transfer when included")),
            ("service_confirmation", _("Service confirmation")),
            ("guest_feedback", _("Guest feedback")),
        ),
    ),
)

HOSTING_SERVICE_CHOICES = tuple(
    choice
    for _group_code, _group_label, group_choices in HOSTING_SERVICE_GROUPS
    for choice in group_choices
)


def default_enabled_hosting_services():
    return []


class Main_things(models.Model):
    """The single administrative source for public identity and brand settings.

    The legacy model and columns are retained to preserve the existing table and
    data. New code must use the canonical fields below.
    """

    CURRENCY_CHOICES = (("USD", "USD"), ("AFN", "AFN"), ("EUR", "EUR"))
    SCHEME_CHOICES = (("https", "HTTPS"), ("http", "HTTP"))
    REQUIRED_PUBLIC_FIELDS = (
        "official_brand_name",
        "short_brand_name",
        "dari_brand_name",
        "primary_tagline",
        "hero_heading",
        "hero_description",
        "legal_entity_name",
        "operating_company_name",
        "office_address",
        "office_city",
        "office_country",
        "primary_email",
        "primary_phone",
        "primary_domain",
        "logo_primary",
        "logo_reversed",
        "logo_symbol",
        "favicon",
        "default_social_image",
    )

    singleton_key = models.PositiveSmallIntegerField(
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    # Existing columns are preserved for data compatibility only.
    noumber = models.CharField(max_length=100, blank=True, default="")
    email = models.CharField(max_length=100, blank=True, default="")

    official_brand_name = models.CharField(
        max_length=160,
        default="Larmoond Travel and Tours",
    )
    short_brand_name = models.CharField(max_length=100, default="Larmoond Travel")
    dari_brand_name = models.CharField(max_length=160, default="لارموند تراول و تور")
    primary_tagline = models.CharField(
        max_length=200,
        default="Your Local Host in Afghanistan",
    )
    hero_heading = models.CharField(
        max_length=255,
        default="Afghanistan, hosted by those who call it home.",
    )
    hero_description = models.TextField(blank=True, default="")

    legal_entity_name = models.CharField(max_length=200, blank=True, default="")
    operating_company_name = models.CharField(max_length=200, blank=True, default="")
    licence_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        validators=(validate_licence_number,),
    )
    licence_authority = models.CharField(max_length=200, blank=True, default="")
    licence_document = models.FileField(
        upload_to="brand/licence/",
        blank=True,
        validators=(
            FileExtensionValidator(("pdf", "jpg", "jpeg", "png")),
            validate_brand_asset_size,
        ),
    )
    office_address = models.TextField(blank=True, default="")
    office_city = models.CharField(max_length=120, blank=True, default="")
    office_country = models.CharField(max_length=120, blank=True, default="")

    primary_email = models.EmailField(blank=True, default="")
    booking_email = models.EmailField(blank=True, default="")
    support_email = models.EmailField(blank=True, default="")
    primary_phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        validators=(validate_phone_number,),
    )
    secondary_phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        validators=(validate_phone_number,),
    )
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        default="",
        validators=(validate_phone_number,),
    )
    business_hours = models.TextField(blank=True, default="")
    emergency_operations_phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        validators=(validate_phone_number,),
    )

    primary_domain = models.CharField(
        max_length=253,
        blank=True,
        default="",
        validators=(validate_domain_name,),
    )
    legacy_domain = models.CharField(
        max_length=253,
        blank=True,
        default="afghanawaits.com",
        validators=(validate_domain_name,),
    )
    canonical_scheme = models.CharField(
        max_length=5,
        choices=SCHEME_CHOICES,
        default="https",
    )

    facebook_url = models.URLField(blank=True, default="")
    instagram_url = models.URLField(blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    youtube_url = models.URLField(blank=True, default="")
    tripadvisor_url = models.URLField(blank=True, default="")

    logo_primary = models.FileField(
        upload_to="brand/logos/",
        blank=True,
        validators=(
            FileExtensionValidator(("svg", "webp", "png")),
            validate_brand_asset_size,
        ),
    )
    logo_reversed = models.FileField(
        upload_to="brand/logos/",
        blank=True,
        validators=(
            FileExtensionValidator(("svg", "webp", "png")),
            validate_brand_asset_size,
        ),
    )
    logo_monochrome = models.FileField(
        upload_to="brand/logos/",
        blank=True,
        validators=(
            FileExtensionValidator(("svg", "webp", "png")),
            validate_brand_asset_size,
        ),
    )
    logo_symbol = models.FileField(
        upload_to="brand/icons/",
        blank=True,
        validators=(
            FileExtensionValidator(("svg", "webp", "png")),
            validate_brand_asset_size,
        ),
    )
    favicon = models.FileField(
        upload_to="brand/icons/",
        blank=True,
        validators=(
            FileExtensionValidator(("ico", "svg", "png")),
            validate_brand_asset_size,
        ),
    )
    default_social_image = models.FileField(
        upload_to="brand/social/",
        blank=True,
        validators=(
            FileExtensionValidator(("jpg", "jpeg", "png", "webp")),
            validate_brand_asset_size,
        ),
    )

    show_licence_badge = models.BooleanField(default=False)
    show_team_section = models.BooleanField(default=False)
    show_reviews = models.BooleanField(default=False)
    show_fixed_departures = models.BooleanField(default=False)
    active_public_languages = models.JSONField(default=default_public_languages)
    default_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="USD",
    )
    enquiry_response_text = models.TextField(blank=True, default="")
    safety_notice = models.TextField(blank=True, default="")
    enabled_hosting_services = models.JSONField(
        default=default_enabled_hosting_services,
        blank=True,
    )
    minimum_featured_tours_for_launch = models.PositiveSmallIntegerField(
        default=3,
        validators=(MinValueValidator(1), MaxValueValidator(12)),
        help_text="Minimum complete, published homepage features required before launch.",
    )

    class Meta:
        verbose_name = "Site and brand configuration"
        verbose_name_plural = "Site and brand configuration"
        permissions = (
            ("manage_site_configuration", "Can manage site and brand configuration"),
        )

    def __str__(self):
        return self.official_brand_name or "Site and brand configuration"

    @classmethod
    def get_solo(cls):
        return (
            cls.objects.filter(singleton_key=1).first()
            or cls.objects.order_by("-pk").first()
            or cls()
        )

    def clean(self):
        super().clean()
        errors = {}

        for field_name in ("primary_domain", "legacy_domain"):
            value = getattr(self, field_name, "")
            if value:
                setattr(self, field_name, value.strip().lower().rstrip("."))

        for field_name in ("primary_email", "booking_email", "support_email"):
            value = getattr(self, field_name, "")
            if value and value.rsplit("@", 1)[-1].lower() in PLACEHOLDER_DOMAINS:
                errors[field_name] = "Use a verified operational email address, not a placeholder."

        if self.primary_domain and self.primary_domain == self.legacy_domain:
            errors["primary_domain"] = "The primary and legacy domains must be different."

        licence_values_present = bool(
            self.licence_number or self.licence_authority or self.licence_document
        )
        if licence_values_present or self.show_licence_badge:
            if not self.licence_number:
                errors["licence_number"] = "Enter the issued licence number."
            if not self.licence_authority:
                errors["licence_authority"] = "Enter the authority that issued the licence."

        language_codes = self.active_public_languages
        available_codes = {code for code, _label in settings.LANGUAGES}
        if not isinstance(language_codes, list) or not language_codes:
            errors["active_public_languages"] = "Select at least one public language."
        else:
            unsupported = sorted(set(language_codes) - available_codes)
            if unsupported:
                errors["active_public_languages"] = (
                    "Unsupported language code(s): " + ", ".join(unsupported)
                )
            elif settings.LANGUAGE_CODE not in language_codes:
                errors["active_public_languages"] = (
                    "The default Django language must remain publicly active."
                )
            elif len(language_codes) != len(set(language_codes)):
                errors["active_public_languages"] = "Public language codes must be unique."

        service_codes = self.enabled_hosting_services
        valid_service_codes = {code for code, _label in HOSTING_SERVICE_CHOICES}
        if not isinstance(service_codes, list):
            errors["enabled_hosting_services"] = "Select hosting services from the approved list."
        else:
            unsupported_services = sorted(set(service_codes) - valid_service_codes)
            if unsupported_services:
                errors["enabled_hosting_services"] = (
                    "Unsupported hosting service code(s): "
                    + ", ".join(unsupported_services)
                )
            elif len(service_codes) != len(set(service_codes)):
                errors["enabled_hosting_services"] = "Hosting service codes must be unique."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        if self._state.adding:
            existing = type(self).objects.filter(singleton_key=1).first()
            if existing and self.pk != existing.pk:
                self.pk = existing.pk
                self._state.adding = False
                kwargs.pop("force_insert", None)
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("The site and brand configuration cannot be deleted.")

    @property
    def missing_required_public_fields(self):
        missing = [
            field_name
            for field_name in self.REQUIRED_PUBLIC_FIELDS
            if not getattr(self, field_name, None)
        ]
        if self.show_licence_badge:
            missing.extend(
                field_name
                for field_name in ("licence_number", "licence_authority")
                if not getattr(self, field_name, None)
            )
        return tuple(dict.fromkeys(missing))

    @property
    def missing_required_public_field_labels(self):
        return tuple(
            self._meta.get_field(field_name).verbose_name.title()
            for field_name in self.missing_required_public_fields
        )

    @property
    def is_public_ready(self):
        return not self.missing_required_public_fields

    @property
    def enabled_hosting_service_groups(self):
        enabled_codes = set(self.enabled_hosting_services or ())
        return tuple(
            {
                "code": group_code,
                "label": group_label,
                "services": tuple(
                    {"code": code, "label": label}
                    for code, label in group_choices
                    if code in enabled_codes
                ),
            }
            for group_code, group_label, group_choices in HOSTING_SERVICE_GROUPS
            if any(code in enabled_codes for code, _label in group_choices)
        )

    @property
    def canonical_origin(self):
        if not self.primary_domain:
            return ""
        return f"{self.canonical_scheme}://{self.primary_domain}"

    def canonical_url(self, path="/"):
        if not self.canonical_origin:
            return ""
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.canonical_origin}{normalized_path}"

    @staticmethod
    def _file_url(file_field):
        if not file_field:
            return ""
        try:
            return file_field.url
        except ValueError:
            return ""

    @property
    def logo_primary_url(self):
        return self._file_url(self.logo_primary)

    @property
    def logo_reversed_url(self):
        return self._file_url(self.logo_reversed)

    @property
    def logo_monochrome_url(self):
        return self._file_url(self.logo_monochrome)

    @property
    def logo_symbol_url(self):
        return self._file_url(self.logo_symbol)

    @property
    def favicon_url(self):
        return self._file_url(self.favicon)

    @property
    def default_social_image_url(self):
        return self._file_url(self.default_social_image)

    @staticmethod
    def _telephone_href(value):
        if not value:
            return ""
        prefix = "+" if value.strip().startswith("+") else ""
        digits = "".join(character for character in value if character.isdigit())
        return f"{prefix}{digits}"

    @property
    def primary_phone_href(self):
        return self._telephone_href(self.primary_phone)

    @property
    def secondary_phone_href(self):
        return self._telephone_href(self.secondary_phone)

    @property
    def emergency_operations_phone_href(self):
        return self._telephone_href(self.emergency_operations_phone)

    @property
    def whatsapp_url(self):
        digits = "".join(
            character for character in self.whatsapp_number if character.isdigit()
        )
        return f"https://wa.me/{digits}" if digits else ""

    @property
    def social_links(self):
        definitions = (
            ("Facebook", self.facebook_url, "fa-brands fa-facebook-f"),
            ("Instagram", self.instagram_url, "fa-brands fa-instagram"),
            ("LinkedIn", self.linkedin_url, "fa-brands fa-linkedin-in"),
            ("YouTube", self.youtube_url, "fa-brands fa-youtube"),
            ("Tripadvisor", self.tripadvisor_url, "fa-solid fa-circle-info"),
        )
        return tuple(item for item in definitions if item[1])


class TourHomepageFeature(models.Model):
    PHYSICAL_LEVEL_CHOICES = (
        ("easy", _("Easy")),
        ("moderate", _("Moderate")),
        ("active", _("Active")),
        ("challenging", _("Challenging")),
    )

    tour = models.OneToOneField(
        "tour.Tour",
        on_delete=models.CASCADE,
        related_name="homepage_feature",
    )
    physical_level = models.CharField(max_length=20, choices=PHYSICAL_LEVEL_CHOICES)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "tour__title", "pk")
        verbose_name = "Homepage tour feature"
        verbose_name_plural = "Homepage tour features"

    def __str__(self):
        return f"Homepage feature · {self.tour}"

    @property
    def route_label(self):
        return " · ".join(self.tour.location or ())

    @property
    def public_type_label(self):
        if self.tour.type == "schedule":
            return _("Scheduled tour")
        return _("On request / flexible dates")

    @property
    def next_departure(self):
        if (
            self.tour.type == "schedule"
            and self.tour.start_date
            and self.tour.start_date >= timezone.localdate()
        ):
            return self.tour.start_date
        return None


class ContentSection(models.Model):
    key = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Stable identifier used by templates, for example home_destinations.",
    )
    name = models.CharField(max_length=150, help_text="Internal management label.")
    eyebrow = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    button_label = models.CharField(max_length=120, blank=True)
    button_url_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Optional named Django URL, for example home:search.",
    )
    button_external_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="content/sections/", blank=True)
    static_image = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "name", "pk")

    def __str__(self):
        return self.name

    @property
    def button_url(self):
        return _resolved_url(self.button_url_name, self.button_external_url)

    @property
    def image_url(self):
        return _resolved_image(self.image, self.static_image)


class ContentItem(models.Model):
    section = models.ForeignKey(
        ContentSection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    icon_class = models.CharField(
        max_length=150,
        blank=True,
        help_text="Optional icon CSS classes, for example fa-solid fa-bed.",
    )
    image = models.ImageField(upload_to="content/items/", blank=True)
    static_image = models.CharField(max_length=255, blank=True)
    link_label = models.CharField(max_length=120, blank=True)
    url_name = models.CharField(max_length=150, blank=True)
    external_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "title", "pk")

    def __str__(self):
        return f"{self.section}: {self.title}"

    @property
    def url(self):
        return _resolved_url(self.url_name, self.external_url)

    @property
    def image_url(self):
        return _resolved_image(self.image, self.static_image)


class ProvincePage(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="provinces/heroes/", blank=True)
    static_hero_image = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional path inside the static folder.",
    )
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "pk")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("states:province_detail", kwargs={"slug": self.slug})

    @property
    def image_url(self):
        return _resolved_image(self.hero_image, self.static_hero_image)


class ProvincePageSection(models.Model):
    page = models.ForeignKey(
        ProvincePage,
        on_delete=models.CASCADE,
        related_name="sections",
    )
    heading = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="provinces/sections/", blank=True)
    static_image = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "heading", "pk")

    def __str__(self):
        return f"{self.page}: {self.heading}"

    @property
    def image_url(self):
        return _resolved_image(self.image, self.static_image)


class ManagedMedia(models.Model):
    CATEGORY_CHOICES = (
        ("image", "Image"),
        ("document", "Document"),
        ("video", "Video"),
        ("other", "Other"),
    )

    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="content/library/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="image")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "title")
        verbose_name_plural = "Managed media"

    def __str__(self):
        return self.title


class PopularPlace(models.Model):
    title = models.CharField(max_length=200, verbose_name="Destination name")
    province = models.CharField(max_length=100, verbose_name="Province", blank=True, null=True)
    preview_image = models.ImageField(
        upload_to="places/previews/",
        verbose_name="Uploaded card image",
        blank=True,
    )
    static_image = models.CharField(
        max_length=255,
        verbose_name="Bundled static image",
        blank=True,
        help_text=(
            "Optional path inside the static folder. The uploaded card image "
            "takes priority when both are set."
        ),
    )
    description = models.TextField(verbose_name="Short description", blank=True, null=True)
    url_name = models.CharField(
        max_length=150,
        verbose_name="Django URL name",
        blank=True,
        help_text="For example: states:kabul or states:Nangarhar",
    )
    external_url = models.URLField(
        verbose_name="External URL",
        blank=True,
        help_text="Optional. When supplied, this link is used instead of the Django URL name.",
    )
    province_page = models.ForeignKey(
        ProvincePage,
        on_delete=models.SET_NULL,
        related_name="popular_cards",
        blank=True,
        null=True,
        help_text="Optional dynamic province page managed in Website Content.",
    )
    display_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="Display order")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "title", "pk")
        verbose_name = "Popular destination"
        verbose_name_plural = "Popular destinations"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        errors = {}
        if not self.preview_image and not self.static_image:
            errors["preview_image"] = "Upload a card image or provide a bundled static image path."
        if not self.external_url and not self.province_page:
            if not self.url_name:
                errors["url_name"] = "Provide a Django URL name or an external URL."
            else:
                try:
                    reverse(self.url_name)
                except NoReverseMatch:
                    errors["url_name"] = "This Django URL name could not be resolved."
        if errors:
            raise ValidationError(errors)

    @property
    def url(self):
        if self.external_url:
            return self.external_url
        if self.province_page:
            return self.province_page.get_absolute_url()
        try:
            return reverse(self.url_name)
        except NoReverseMatch:
            return "#"

    @property
    def image_url(self):
        return _resolved_image(self.preview_image, self.static_image)


class PlaceImage(models.Model):
    place = models.ForeignKey(PopularPlace, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="places/gallery/", verbose_name="Gallery image")

    def __str__(self):
        return f"Image for {self.place.title}"


class TripRequest(models.Model):
    STATUS_CHOICES = (
        ("submitted", "Submitted"),
        ("under_review", "Under review"),
        ("proposal_sent", "Proposal sent"),
        ("changes_requested", "Changes requested"),
        ("approved", "Approved"),
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
    )
    PACE_CHOICES = (
        ("relaxed", "Relaxed"),
        ("balanced", "Balanced"),
        ("active", "Active"),
    )
    BUDGET_CHOICES = (
        ("economy", "Economy"),
        ("comfort", "Comfort"),
        ("premium", "Premium"),
        ("luxury", "Luxury"),
        ("flexible", "Flexible / advise me"),
    )

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user_id = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=30)
    country_of_origin = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    budget_tier = models.CharField(max_length=20, choices=BUDGET_CHOICES, default="flexible")
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pace = models.CharField(max_length=20, choices=PACE_CHOICES, default="balanced")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="submitted", db_index=True)
    assigned_expert_id = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    booking_id = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    submitted_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-submitted_at", "-pk")
        verbose_name = "Custom trip request"
        verbose_name_plural = "Custom trip requests"

    def __str__(self):
        return f"{self.reference} · {self.full_name}"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})

    @property
    def reference(self):
        return f"TR-{str(self.public_id).split('-')[0].upper()}"

    @property
    def traveller_count(self):
        return self.adults + self.children

    @property
    def duration_days(self):
        if not self.start_date or not self.end_date:
            return 0
        return (self.end_date - self.start_date).days + 1

    @property
    def customer_user(self):
        if not self.user_id:
            return None
        return get_user_model().objects.filter(pk=self.user_id).first()

    @property
    def assigned_expert(self):
        if not self.assigned_expert_id:
            return None
        return get_user_model().objects.filter(pk=self.assigned_expert_id).first()

    @property
    def booking(self):
        if not self.booking_id:
            return None
        from tour.models import Booking

        return Booking.objects.filter(pk=self.booking_id).first()

    def get_absolute_url(self):
        return reverse("home:trip_request_detail", kwargs={"public_id": self.public_id})


class TripStop(models.Model):
    trip_request = models.ForeignKey(TripRequest, on_delete=models.CASCADE, related_name="stops")
    destination = models.ForeignKey(PopularPlace, on_delete=models.PROTECT, related_name="trip_stops")
    position = models.PositiveSmallIntegerField(default=1)
    nights = models.PositiveSmallIntegerField(default=1)
    notes = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ("position", "pk")
        constraints = (
            models.UniqueConstraint(fields=("trip_request", "position"), name="home_tripstop_unique_position"),
            models.UniqueConstraint(fields=("trip_request", "destination"), name="home_tripstop_unique_destination"),
        )

    def __str__(self):
        return f"{self.trip_request.reference} · {self.position}. {self.destination}"


class TripPreference(models.Model):
    ACCOMMODATION_CHOICES = (
        ("hotel", "Hotel"),
        ("guesthouse", "Guesthouse"),
        ("homestay", "Homestay"),
        ("mixed", "A suitable mix"),
        ("advise", "Advise me"),
    )
    TRANSPORT_CHOICES = (
        ("private", "Private vehicle"),
        ("shared", "Shared transport"),
        ("flight", "Domestic flight where practical"),
        ("mixed", "Best practical mix"),
        ("advise", "Advise me"),
    )

    trip_request = models.OneToOneField(TripRequest, on_delete=models.CASCADE, related_name="preferences")
    interests = models.JSONField(default=list, blank=True)
    accommodation_type = models.CharField(max_length=20, choices=ACCOMMODATION_CHOICES, default="advise")
    transport_preference = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default="advise")
    needs_local_guide = models.BooleanField(default=True)
    needs_translator = models.BooleanField(default=False)
    accessibility_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Preferences · {self.trip_request.reference}"


class EntryPlan(models.Model):
    SELECTION_CHOICES = (
        ("self", "I will choose my entry point"),
        ("recommend", "Recommend the best entry point"),
        ("flexible", "Air or land — choose for me"),
    )
    TRANSPORT_CHOICES = (
        ("air", "Air"),
        ("land", "Land"),
        ("either", "Either / advise me"),
    )
    STATUS_CHOICES = (
        ("pending", "Needs review"),
        ("recommended", "Recommendation prepared"),
        ("confirmed", "Confirmed"),
    )
    ENTRY_POINT_CHOICES = (
        ("", "Select an entry point"),
        ("kabul_airport", "Kabul International Airport"),
        ("herat_airport", "Herat International Airport"),
        ("mazar_airport", "Mazar-i-Sharif Airport"),
        ("kandahar_airport", "Kandahar Airport"),
        ("torkham_border", "Torkham Border (Pakistan)"),
        ("spin_boldak", "Spin Boldak (Pakistan)"),
        ("islam_qala", "Islam Qala (Iran)"),
        ("hairatan", "Hairatan (Uzbekistan)"),
        ("torghundi", "Torghundi (Turkmenistan)"),
        ("other", "Other"),
    )

    trip_request = models.OneToOneField(TripRequest, on_delete=models.CASCADE, related_name="entry_plan")
    selection_mode = models.CharField(max_length=20, choices=SELECTION_CHOICES, default="recommend")
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default="either")
    arrival_origin = models.CharField(max_length=150, help_text="Country or city the traveller expects to arrive from.")
    selected_entry_point = models.CharField(max_length=50, choices=ENTRY_POINT_CHOICES, blank=True)
    other_entry_point = models.CharField(max_length=150, blank=True)
    recommended_entry_point = models.CharField(max_length=150, blank=True)
    alternatives = models.TextField(blank=True)
    operator_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    confirmed_by_id = models.PositiveBigIntegerField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Entry plan · {self.trip_request.reference}"

    @property
    def selected_entry_point_label(self):
        if self.selected_entry_point == "other":
            return self.other_entry_point
        return self.get_selected_entry_point_display() if self.selected_entry_point else ""


class RouteProposal(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("sent", "Sent to traveller"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    )
    CURRENCY_CHOICES = (("USD", "USD"), ("AFN", "AFN"), ("EUR", "EUR"))

    trip_request = models.ForeignKey(TripRequest, on_delete=models.CASCADE, related_name="proposals")
    version = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    proposed_entry_point = models.CharField(max_length=150)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    valid_until = models.DateField(blank=True, null=True)
    customer_message = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    booking_tour_id = models.PositiveBigIntegerField(blank=True, null=True)
    created_by_id = models.PositiveBigIntegerField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-version", "-created_at")
        constraints = (
            models.UniqueConstraint(fields=("trip_request", "version"), name="home_routeproposal_unique_version"),
        )

    def __str__(self):
        return f"{self.trip_request.reference} · proposal v{self.version}"

    @property
    def booking_tour(self):
        if not self.booking_tour_id:
            return None
        from tour.models import Tour

        return Tour.objects.filter(pk=self.booking_tour_id).first()


class RouteProposalDay(models.Model):
    proposal = models.ForeignKey(RouteProposal, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveSmallIntegerField()
    destination = models.ForeignKey(PopularPlace, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    overnight_location = models.CharField(max_length=150, blank=True)
    transport = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ("day_number", "pk")
        constraints = (
            models.UniqueConstraint(fields=("proposal", "day_number"), name="home_proposalday_unique_day"),
        )

    def __str__(self):
        return f"{self.proposal} · day {self.day_number}"
