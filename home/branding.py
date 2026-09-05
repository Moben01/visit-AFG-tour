import re


OFFICIAL_BRAND_NAME = "Larmoond Travel and Tours"
SHORT_BRAND_NAME = "Larmoond Travel"
PRIMARY_TAGLINE = "Your Local Host in Afghanistan"

LEGACY_PUBLIC_TERMS = (
    "visa-support@afghanistan.travel",
    "info@afghanawaits.com",
    "Visit Afghanistan Tours",
    "Every Journey Together",
    "AfghanAwaits.com",
    "Afghan Awaits",
    "AfghanAwaits",
    "Visit Afghanistan",
    "afghanistan.travel",
)

PROHIBITED_BRAND_VARIANTS = (
    "Larmoond Tours and Travel",
    "Larmond",
    "Larmoond Travel & Tour",
    "Larmoond Trous",
)

AUDITED_BRAND_TERMS = LEGACY_PUBLIC_TERMS + PROHIBITED_BRAND_VARIANTS

_NORMALIZED_TERMS = {term.casefold(): term for term in AUDITED_BRAND_TERMS}
_TERM_PATTERN = re.compile(
    "|".join(re.escape(term) for term in sorted(AUDITED_BRAND_TERMS, key=len, reverse=True)),
    re.IGNORECASE,
)

_REPLACEMENTS = {
    "every journey together": PRIMARY_TAGLINE,
    "info@afghanawaits.com": "",
    "visa-support@afghanistan.travel": "",
    "afghanistan.travel": "",
}


DATABASE_AUDIT_FIELDS = {
    "home.Main_things": (
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
        "booking_email",
        "support_email",
        "business_hours",
        "enquiry_response_text",
        "safety_notice",
    ),
    "home.ContentSection": ("name", "eyebrow", "title", "body", "button_label"),
    "home.ContentItem": ("title", "subtitle", "body", "link_label"),
    "home.ProvincePage": ("name", "summary", "body", "meta_title", "meta_description"),
    "home.ProvincePageSection": ("heading", "body"),
    "home.ManagedMedia": ("title", "alt_text"),
    "home.PopularPlace": ("title", "description"),
    "home.RouteProposal": ("title", "summary", "customer_message"),
    "home.RouteProposalDay": ("title", "description", "overnight_location", "transport"),
    "tour.TourCategory": ("name", "description"),
    "tour.Tour": ("title", "description", "location"),
    "tour.Accommodation": ("name", "description", "location", "address", "email", "website"),
    "tour.ItineraryItem": ("title", "description", "type_of_transport"),
    "tour.UserItineraryItem": ("title", "description", "type_of_transport"),
    "tour.Frequently_asked_questions": ("question", "answer"),
    "tour.Includes": ("title",),
    "tour.Excludes": ("title",),
    "tour.TrainingCourse": ("title", "description", "content"),
    "tour.CrewNotification": ("title", "message"),
    "things_to_do.Best_places_for_visit": ("title", "description", "location"),
    "things_to_do.Top_things_to_do_in_province": ("title", "description", "location"),
    "things_to_do.Popular_Tourist": ("title", "description", "location"),
    "things_to_do.Best_Selling": ("title", "description", "location"),
}

# This deliberately omits account identities, identifiers, file fields, private
# notes, notifications, service orders, supplier invoices and payment history.
DATABASE_REPLACEMENT_FIELDS = {
    label: fields
    for label, fields in DATABASE_AUDIT_FIELDS.items()
    if label
    not in {
        "tour.UserItineraryItem",
        "tour.CrewNotification",
    }
}


def iter_brand_matches(value):
    if not isinstance(value, str) or not value:
        return
    for match in _TERM_PATTERN.finditer(value):
        matched = match.group(0)
        yield _NORMALIZED_TERMS[matched.casefold()]


def replace_brand_terms(value):
    if not isinstance(value, str) or not value:
        return value

    def replacement(match):
        normalized = match.group(0).casefold()
        return _REPLACEMENTS.get(normalized, OFFICIAL_BRAND_NAME)

    replaced = _TERM_PATTERN.sub(replacement, value)
    replaced = re.sub(r"[ \t]{2,}", " ", replaced)
    replaced = re.sub(r"[ \t]+([,.;:])", r"\1", replaced)
    return replaced.strip() if replaced != value else value
