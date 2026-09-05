from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import HOSTING_SERVICE_CHOICES, Main_things


class SiteConfigurationAdminForm(forms.ModelForm):
    active_public_languages = forms.MultipleChoiceField(
        choices=(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Only configured Django languages can be selected.",
    )
    enabled_hosting_services = forms.MultipleChoiceField(
        choices=HOSTING_SERVICE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=(
            "Select only services the operations team has confirmed it can deliver. "
            "Unselected services are omitted from the public homepage."
        ),
    )

    class Meta:
        model = Main_things
        fields = "__all__"
        widgets = {
            "hero_description": forms.Textarea(attrs={"rows": 3}),
            "office_address": forms.Textarea(attrs={"rows": 3}),
            "business_hours": forms.Textarea(attrs={"rows": 3}),
            "enquiry_response_text": forms.Textarea(attrs={"rows": 3}),
            "safety_notice": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["active_public_languages"].choices = settings.LANGUAGES
        if self.instance:
            self.initial["active_public_languages"] = (
                self.instance.active_public_languages or []
            )
            self.initial["enabled_hosting_services"] = (
                self.instance.enabled_hosting_services or []
            )

    def clean_active_public_languages(self):
        return list(self.cleaned_data["active_public_languages"])

    def clean_enabled_hosting_services(self):
        return list(self.cleaned_data["enabled_hosting_services"])


class SiteConfigurationAdmin(admin.ModelAdmin):
    form = SiteConfigurationAdminForm
    readonly_fields = ("readiness_status",)
    fieldsets = (
        ("Public-site readiness", {"fields": ("readiness_status",)}),
        (
            "Brand",
            {
                "fields": (
                    "official_brand_name",
                    "short_brand_name",
                    "dari_brand_name",
                    "primary_tagline",
                    "hero_heading",
                    "hero_description",
                )
            },
        ),
        (
            "Legal identity",
            {
                "fields": (
                    "legal_entity_name",
                    "operating_company_name",
                    "licence_number",
                    "licence_authority",
                    "licence_document",
                    "office_address",
                    "office_city",
                    "office_country",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "primary_email",
                    "booking_email",
                    "support_email",
                    "primary_phone",
                    "secondary_phone",
                    "whatsapp_number",
                    "business_hours",
                    "emergency_operations_phone",
                )
            },
        ),
        (
            "Domains",
            {"fields": ("primary_domain", "legacy_domain", "canonical_scheme")},
        ),
        (
            "Social profiles",
            {
                "fields": (
                    "facebook_url",
                    "instagram_url",
                    "linkedin_url",
                    "youtube_url",
                    "tripadvisor_url",
                )
            },
        ),
        (
            "Approved brand assets",
            {
                "description": (
                    "Upload only official supplied assets. SVG, WEBP, PNG and ICO "
                    "files are accepted where appropriate; do not upload redrawn logos."
                ),
                "fields": (
                    "logo_primary",
                    "logo_reversed",
                    "logo_monochrome",
                    "logo_symbol",
                    "favicon",
                    "default_social_image",
                ),
            },
        ),
        (
            "Operational display settings",
            {
                "fields": (
                    "show_licence_badge",
                    "show_team_section",
                    "show_reviews",
                    "show_fixed_departures",
                    "enabled_hosting_services",
                    "minimum_featured_tours_for_launch",
                    "active_public_languages",
                    "default_currency",
                    "enquiry_response_text",
                    "safety_notice",
                )
            },
        ),
    )

    def _has_configuration_permission(self, request):
        return (
            request.user.is_active
            and request.user.is_staff
            and request.user.has_perm("home.manage_site_configuration")
        )

    def has_module_permission(self, request):
        return self._has_configuration_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._has_configuration_permission(request)

    def has_add_permission(self, request):
        return self._has_configuration_permission(request) and not Main_things.objects.filter(
            singleton_key=1
        ).exists()

    def has_change_permission(self, request, obj=None):
        return self._has_configuration_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(singleton_key=1)

    @admin.display(description="Readiness")
    def readiness_status(self, obj):
        if not obj or obj.is_public_ready:
            return format_html(
                '<strong style="color:#1b5e20">{}</strong>',
                "Public-site required fields are complete.",
            )
        return format_html(
            '<div style="color:#8a4b00"><strong>Public-site setup is incomplete.</strong>'
            "<br>Missing: {}</div>",
            ", ".join(obj.missing_required_public_field_labels),
        )

    def changelist_view(self, request, extra_context=None):
        if not self._has_configuration_permission(request):
            raise PermissionDenied
        configuration = Main_things.objects.filter(singleton_key=1).first()
        if configuration:
            return redirect(
                reverse(
                    f"{self.admin_site.name}:home_main_things_change",
                    args=(configuration.pk,),
                )
            )
        return redirect(reverse(f"{self.admin_site.name}:home_main_things_add"))

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        configuration = None
        if object_id:
            configuration = Main_things.objects.filter(pk=object_id, singleton_key=1).first()
        if request.method == "GET" and configuration and not configuration.is_public_ready:
            messages.warning(
                request,
                "Public-site readiness warning: missing "
                + ", ".join(configuration.missing_required_public_field_labels)
                + ". Empty values are not displayed publicly.",
            )
        return super().changeform_view(request, object_id, form_url, extra_context)


site_configuration_admin = admin.AdminSite(name="site_configuration_admin")
site_configuration_admin.site_header = "Larmoond Travel administration"
site_configuration_admin.site_title = "Larmoond Travel administration"
site_configuration_admin.index_title = "Restricted site configuration"
site_configuration_admin.register(Main_things, SiteConfigurationAdmin)
