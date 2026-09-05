from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .models import Main_things


class PublicShellTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()
        self.configuration = Main_things.objects.create(
            active_public_languages=["en"],
        )

    def _home_sections(self):
        response = self.client.get(reverse("home:home"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        header = body[body.index("<header"):body.index("</header>")]
        footer = body[body.index("<footer"):body.index("</footer>")]
        return response, header, footer

    def test_primary_navigation_uses_required_labels_existing_routes_and_order(self):
        _response, header, footer = self._home_sections()
        expected_labels = (
            "Home",
            "Tours",
            "Destinations",
            "Experiences",
            "Plan Your Trip",
            "About Us",
            "Contact",
        )
        positions = [header.index(f">{label}</a>") for label in expected_labels]

        self.assertEqual(positions, sorted(positions))
        self.assertIn(f'href="{reverse("home:home")}#tours"', header)
        self.assertIn(f'href="{reverse("home:home")}#destinations"', header)
        self.assertIn(f'href="{reverse("things_to_do:Experiences")}"', header)
        self.assertIn(f'href="{reverse("home:trip_builder")}"', header)
        self.assertIn(f'href="{reverse("states:team")}"', header)
        self.assertNotIn("Become an Expert", header)
        self.assertIn("Work With Us", footer)
        self.assertIn("Become an Expert", footer)

    def test_mobile_menu_and_current_page_markup_are_accessible(self):
        _response, header, _footer = self._home_sections()

        self.assertIn('<nav class="lm-primary-navigation collapse"', header)
        self.assertIn('aria-label="Primary navigation"', header)
        self.assertIn('aria-controls="larmoondPrimaryNavigation"', header)
        self.assertIn('aria-expanded="false"', header)
        self.assertIn('aria-label="Open navigation menu"', header)
        self.assertIn('aria-current="page"', header)
        self.assertIn('data-close-label="Close navigation menu"', header)

    def test_primary_logo_and_compact_mobile_variant_come_from_site_settings(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(
            logo_primary="brand/logos/test-primary.svg",
            logo_symbol="brand/icons/test-symbol.svg",
        )

        _response, header, _footer = self._home_sections()

        self.assertIn('class="lm-brand-logo" src="/media/brand/logos/test-primary.svg"', header)
        self.assertIn('class="lm-brand-symbol" src="/media/brand/icons/test-symbol.svg"', header)

    def test_language_switcher_only_contains_languages_marked_active(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(
            active_public_languages=["en", "fa"],
        )

        _response, header, _footer = self._home_sections()

        self.assertIn('name="language" value="en"', header)
        self.assertIn('name="language" value="fa"', header)
        self.assertNotIn('name="language" value="ar"', header)

    def test_missing_contact_and_licence_values_do_not_render_empty_labels(self):
        _response, header, footer = self._home_sections()

        for missing_label in ("Email", "Bookings", "Telephone", "WhatsApp", "Business hours", "Licensed by"):
            with self.subTest(missing_label=missing_label):
                self.assertNotIn(f">{missing_label}<", footer)
        self.assertNotIn('href="mailto:', footer)
        self.assertNotIn('href="tel:', footer)
        self.assertNotIn('data-analytics-event="whatsapp_contact"', header + footer)

    def test_completed_contact_licence_social_and_whatsapp_settings_render(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(
            primary_email="operations@unit-test.invalid",
            booking_email="bookings@unit-test.invalid",
            primary_phone="+93700000001",
            whatsapp_number="+93700000002",
            business_hours="Test schedule only",
            office_address="Test-only office record",
            office_city="Test city",
            office_country="Test country",
            licence_number="TEST-LICENCE-01",
            licence_authority="Test issuing authority",
            show_licence_badge=True,
            instagram_url="https://social.test/larmoond",
        )

        _response, header, footer = self._home_sections()

        self.assertIn("operations@unit-test.invalid", footer)
        self.assertIn("bookings@unit-test.invalid", footer)
        self.assertIn("+93700000001", footer)
        self.assertIn("Test-only office record, Test city, Test country", footer)
        self.assertIn("Test issuing authority · TEST-LICENCE-01", footer)
        self.assertIn('data-analytics-event="whatsapp_contact"', header)
        self.assertIn('data-analytics-event="whatsapp_contact"', footer)
        self.assertIn('href="https://social.test/larmoond"', footer)

    def test_footer_contains_approved_positioning_policies_and_copyright(self):
        _response, _header, footer = self._home_sections()

        self.assertIn(
            "Larmoond Travel and Tours designs and operates private and small-group "
            "journeys across Afghanistan with local guides, coordinated transport, "
            "clear itineraries, and on-trip support.",
            footer,
        )
        for label in (
            "Privacy",
            "Terms",
            "Cancellation and Refunds",
            "Responsible Travel",
            "Safety Information",
        ):
            self.assertIn(f">{label}</a>", footer)
        self.assertIn("Larmoond Travel and Tours. All rights reserved.", footer)

    def test_private_journey_cta_is_visible_in_desktop_and_mobile_markup(self):
        _response, header, _footer = self._home_sections()

        self.assertEqual(header.count(">Plan a Private Journey</a>"), 2)
        self.assertIn('data-analytics-placement="header_desktop"', header)
        self.assertIn('data-analytics-placement="header_mobile"', header)


class PublicShellAssetTests(TestCase):
    def test_active_non_english_catalogs_translate_new_shell_messages(self):
        required_messages = (
            "About Us",
            "Contact",
            "Plan a Private Journey",
            "Open navigation menu",
            "Work With Us",
            "Responsible Travel",
            "Safety Information",
            "Larmoond Travel and Tours designs and operates private and small-group journeys across Afghanistan with local guides, coordinated transport, clear itineraries, and on-trip support.",
        )

        for language_code in ("fa", "ar"):
            catalog = (
                Path(settings.BASE_DIR)
                / f"home/locale/{language_code}/LC_MESSAGES/django.po"
            ).read_text(encoding="utf-8")
            for message in required_messages:
                with self.subTest(language_code=language_code, message=message):
                    entry_start = catalog.index(f'msgid "{message}"')
                    entry = catalog[entry_start:catalog.find("\n\n", entry_start)]
                    self.assertNotIn('msgstr ""', entry)

    def test_shell_styles_include_mobile_breakpoints_and_visible_focus_states(self):
        source = (Path(settings.BASE_DIR) / "static/css/larmoond-public-shell.css").read_text(
            encoding="utf-8"
        )

        self.assertIn(":focus-visible", source)
        self.assertIn("@media (max-width: 1279.98px)", source)
        self.assertIn("@media (max-width: 575.98px)", source)
        self.assertIn(".lm-header-cta--mobile", source)
        self.assertIn("@media (prefers-reduced-motion: reduce)", source)

    def test_cta_tracking_payload_is_fixed_and_contains_no_personal_data(self):
        source = (Path(settings.BASE_DIR) / "static/js/larmoond-public-shell.js").read_text(
            encoding="utf-8"
        )

        self.assertIn('event: "public_cta_click"', source)
        self.assertIn("action,\n      placement,", source)
        self.assertIn("allowedActions", source)
        self.assertIn("allowedPlacements", source)
        for prohibited_value in (
            "control.href",
            "control.textContent",
            "window.location",
            "document.location",
            "userId",
            "email",
            "phone",
        ):
            with self.subTest(prohibited_value=prohibited_value):
                self.assertNotIn(prohibited_value, source)
