from django.db import migrations


SECTIONS = (
    ("home_map_hero", "Homepage map hero", "Explore Afghanistan", "Every Journey Together", "Choose a place. Follow the route. Discover Afghanistan with local experts by your side.", "Explore destinations", "", 10),
    ("home_benefits", "Homepage benefits", "Why AfghanAwaits", "Plan with local clarity", "Practical destination knowledge, connected planning and travel support.", "", "", 20),
    ("home_destinations", "Homepage destinations", "Destinations", "Popular places in Afghanistan", "Start with a province guide, then connect places into a route that fits your time and interests.", "", "", 30),
    ("home_explore", "Homepage explore", "Explore", "Build your Afghanistan journey", "Choose a published tour when available, or begin with guides and plan a custom route.", "", "", 40),
    ("home_trust", "Homepage process", "Plan with clarity", "From first question to the final travel day", "AfghanAwaits connects information, booking details, and local operations in one clear workflow.", "Start exploring", "home:search", 50),
    ("home_inspiration", "Homepage inspiration", "Travel inspiration", "Know more before you go", "Original Afghan destination and culture content, connected directly to practical planning pages.", "", "", 60),
    ("home_services", "Homepage services", "Plan Your Trip", "One connected itinerary", "Tours, transport, accommodation, documents, and timing in one workflow.", "", "", 70),
    ("home_planning", "Homepage travel guidance", "Before you travel", "Start with current practical guidance", "Review essential information before confirming your route.", "", "", 80),
    ("home_dashboard", "Homepage customer dashboard", "Your trip, connected", "Keep confirmed travel details in one place", "Use your account to follow bookings, payments and travel arrangements.", "Open dashboard", "tour:dashboard", 90),
    ("home_professionals", "Homepage professionals", "Local travel professionals", "Share your expertise through AfghanAwaits", "Join the network of local guides, translators and travel professionals.", "Become an expert", "tour:tour_guide_view", 100),
)


ITEMS = {
    "home_benefits": (
        ("Local destination knowledge", "Province guides built around Afghan places, culture, and practical access.", "fa-solid fa-map-location-dot", "", 10),
        ("One connected itinerary", "Tours, transport, accommodation, documents, and timing in one workflow.", "fa-solid fa-route", "", 20),
        ("Practical travel support", "Clear preparation guidance and local coordination for confirmed services.", "fa-solid fa-shield-halved", "", 30),
    ),
    "home_services": (
        ("Accommodation planning", "Keep suitable stays connected to your route and travel dates.", "fa-solid fa-bed", "play_your_trip:Accommodation", 10),
        ("Local transport", "Understand practical connections between cities and destinations.", "fa-solid fa-car-side", "play_your_trip:Getting_to_around_afg", 20),
        ("Local experts", "Travel knowledge and coordination from people who know the place.", "fa-solid fa-user-check", "tour:tour_guide_view", 30),
    ),
    "home_trust": (
        ("Research", "Read destination, culture, visa, weather, currency, and safety guidance.", "", "", 10),
        ("Confirm", "Review the itinerary, inclusions, dates, provider terms, and price before booking.", "", "", 20),
        ("Coordinate", "Keep booking, pre-arrival information, pickup, and trip details connected.", "", "", 30),
    ),
}


def seed_sections(apps, schema_editor):
    ContentSection = apps.get_model("home", "ContentSection")
    ContentItem = apps.get_model("home", "ContentItem")
    for key, name, eyebrow, title, body, button_label, button_url_name, order in SECTIONS:
        section, _ = ContentSection.objects.get_or_create(
            key=key,
            defaults={
                "name": name,
                "eyebrow": eyebrow,
                "title": title,
                "body": body,
                "button_label": button_label,
                "button_url_name": button_url_name,
                "display_order": order,
                "is_active": True,
            },
        )
        for item_title, item_body, icon_class, url_name, item_order in ITEMS.get(key, ()):
            ContentItem.objects.get_or_create(
                section=section,
                title=item_title,
                defaults={
                    "body": item_body,
                    "icon_class": icon_class,
                    "url_name": url_name,
                    "display_order": item_order,
                    "is_active": True,
                },
            )


class Migration(migrations.Migration):
    dependencies = [("home", "0004_website_content_management")]
    operations = [migrations.RunPython(seed_sections, migrations.RunPython.noop)]
