import json

from django.conf import settings
from django.db import DatabaseError
from django.db.models import Prefetch

from tour.models import TourCategory, User_favorite_tour

from .models import ContentItem, ContentSection, Main_things
from .permissions import has_content_management_access


def _absolute_public_url(request, configuration, value):
    if not value or value.startswith(("http://", "https://")):
        return value
    if configuration.canonical_origin:
        return f"{configuration.canonical_origin}{value}"
    return request.build_absolute_uri(value)


def _organization_json_ld(request, configuration, social_links):
    organization = {
        "@context": "https://schema.org",
        "@type": "TravelAgency",
        "name": configuration.official_brand_name,
    }
    if configuration.short_brand_name:
        organization["alternateName"] = configuration.short_brand_name
    if configuration.primary_tagline:
        organization["slogan"] = configuration.primary_tagline
    if configuration.canonical_origin:
        organization["@id"] = f"{configuration.canonical_origin}/#organization"
        organization["url"] = configuration.canonical_origin
    if configuration.primary_email:
        organization["email"] = configuration.primary_email
    if configuration.primary_phone:
        organization["telephone"] = configuration.primary_phone
    logo_url = _absolute_public_url(
        request, configuration, configuration.logo_primary_url
    )
    if logo_url:
        organization["logo"] = logo_url
    address = {
        "@type": "PostalAddress",
        "streetAddress": configuration.office_address,
        "addressLocality": configuration.office_city,
        "addressCountry": configuration.office_country,
    }
    address = {key: value for key, value in address.items() if value}
    if len(address) > 1:
        organization["address"] = address
    same_as = [url for _label, url, _icon in social_links]
    if same_as:
        organization["sameAs"] = same_as
    serialized = json.dumps(organization, ensure_ascii=False, separators=(",", ":"))
    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def site_navigation(request):
    try:
        categories = TourCategory.objects.all()[:12]
        favorite_count = (
            User_favorite_tour.objects.filter(user=request.user, favorite=True).count()
            if request.user.is_authenticated
            else 0
        )
    except DatabaseError:
        categories = ()
        favorite_count = 0

    try:
        visible_items = ContentItem.objects.filter(is_active=True).order_by(
            "display_order", "title", "pk"
        )
        section_queryset = ContentSection.objects.filter(is_active=True).prefetch_related(
            Prefetch("items", queryset=visible_items, to_attr="visible_items")
        )
        site_sections = {section.key: section for section in section_queryset}
        site_config = Main_things.get_solo()
    except DatabaseError:
        site_sections = {}
        site_config = Main_things()

    active_language_codes = set(site_config.active_public_languages or ())
    public_languages = tuple(
        (code, label)
        for code, label in settings.LANGUAGES
        if code in active_language_codes
    )
    current_language_code = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    current_language_label = next(
        (label for code, label in public_languages if code == current_language_code),
        "",
    )
    canonical_url = site_config.canonical_url(request.path)
    social_image_url = _absolute_public_url(
        request, site_config, site_config.default_social_image_url
    )
    social_links = site_config.social_links

    return {
        "get_tour_categories": categories,
        "find_user_favorite": favorite_count,
        "site_currency": request.session.get(
            "currency", site_config.default_currency or "USD"
        ),
        "site_config": site_config,
        "get_main_things": site_config,
        "site_public_languages": public_languages,
        "site_current_language_label": current_language_label,
        "site_canonical_url": canonical_url,
        "site_default_social_image_url": social_image_url,
        "site_social_links": social_links,
        "site_organization_json_ld": _organization_json_ld(
            request, site_config, social_links
        ),
        "site_sections": site_sections,
        "can_manage_website_content": has_content_management_access(request.user),
    }
