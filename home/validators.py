import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s().-]{6,24}$")
DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$",
    re.IGNORECASE,
)
LICENCE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ./_-]{1,99}$")

PLACEHOLDER_TEXT = {"n/a", "na", "none", "not available", "placeholder", "tbc", "tbd", "unknown"}
PLACEHOLDER_DOMAINS = {"example.com", "example.net", "example.org", "test.com"}
PLACEHOLDER_PHONE_DIGITS = {"93123456789"}


def validate_phone_number(value):
    if not value:
        return
    candidate = value.strip()
    digits = re.sub(r"\D", "", candidate)
    if (
        not PHONE_PATTERN.fullmatch(candidate)
        or not 7 <= len(digits) <= 15
        or "x" in candidate.lower()
        or digits in PLACEHOLDER_PHONE_DIGITS
    ):
        raise ValidationError(
            _("Enter a real telephone number using digits and an optional international prefix."),
            code="invalid_phone_number",
        )


def validate_domain_name(value):
    if not value:
        return
    candidate = value.strip().lower().rstrip(".")
    if candidate in PLACEHOLDER_DOMAINS or not DOMAIN_PATTERN.fullmatch(candidate):
        raise ValidationError(
            _("Enter a domain name without a scheme, path, port, or email address."),
            code="invalid_domain_name",
        )


def validate_licence_number(value):
    if not value:
        return
    candidate = value.strip()
    if candidate.lower() in PLACEHOLDER_TEXT or not LICENCE_PATTERN.fullmatch(candidate):
        raise ValidationError(
            _("Enter the issued licence number exactly as it appears on the official document."),
            code="invalid_licence_number",
        )


def validate_brand_asset_size(value):
    if value and value.size > 10 * 1024 * 1024:
        raise ValidationError(
            _("Brand asset files may not exceed 10 MB."),
            code="brand_asset_too_large",
        )
