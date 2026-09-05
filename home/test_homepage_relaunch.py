from datetime import timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tour.models import (
    Booking,
    CrewEngagement,
    CrewMember,
    CrewReview,
    CrewRole,
    ItineraryItem,
    Tour,
    TourCategory,
    TourGuide,
)

from .homepage import public_featured_tours
from .models import Main_things, PopularPlace, TourHomepageFeature


User = get_user_model()


class HomepageRelaunchTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()
        self.configuration = Main_things.objects.create(
            hero_description="Approved homepage configuration",
            active_public_languages=["en"],
        )
        PopularPlace.objects.all().update(is_active=False)
        self.category = TourCategory.objects.create(
            name="Homepage cultural journeys",
            slug="homepage-cultural-journeys",
            icon="ti ti-route",
        )

    def create_tour(self, *, itinerary_days=1, featured=True, **overrides):
        sequence = Tour.objects.count() + 1
        values = {
            "category": self.category,
            "title": f"Public journey {sequence}",
            "image": f"tour-image/public-journey-{sequence}.webp",
            "slug": f"public-journey-{sequence}",
            "type": "not_schedule",
            "description": "A complete local itinerary with clear inclusions.",
            "location": ["Kabul", "Bamyan"],
            "duration_day": str(itinerary_days),
            "duration_night": str(max(0, itinerary_days - 1)),
            "price": Decimal("640.00"),
            "available": True,
            "google_location": "",
        }
        values.update(overrides)
        tour = Tour.objects.create(**values)
        for day_number in range(1, itinerary_days + 1):
            ItineraryItem.objects.create(
                tour=tour,
                day_number=day_number,
                title=f"Day {day_number}",
                description=f"Confirmed itinerary day {day_number}.",
                date=timezone.now() + timedelta(days=day_number - 1),
            )
        if featured:
            TourHomepageFeature.objects.create(
                tour=tour,
                physical_level="moderate",
                display_order=sequence,
                is_active=True,
            )
        return tour

    def create_public_host(self):
        return TourGuide.objects.create(
            name="Approved Host",
            gender="M",
            phone="PRIVATE-PHONE-777",
            email="private-guide@example.test",
            provinces="Bamyan and Kabul",
            languages="Dari, Pashto, English",
            experience_years=7,
            specialties=["cultural"],
            bio="A public professional biography for the approved local host.",
            id_number="PRIVATE-ID-777",
            cv="guides/cv/private-record.pdf",
            profile_image="guides/approved-host.webp",
            is_approved=True,
            is_active=True,
        )

    def test_required_sales_sections_render_in_order_with_exact_core_copy(self):
        self.create_public_host()
        Main_things.objects.filter(pk=self.configuration.pk).update(
            show_team_section=True
        )

        response = self.client.get(reverse("home:home"))
        page = response.content.decode()
        markers = (
            "Afghanistan, hosted by those who call it home.",
            "Journeys ready to explore",
            "More than a tour. Your local host in Afghanistan.",
            "From first request to local welcome",
            "Support connected to each stage of your journey",
            "Places to begin your Afghanistan journey",
            "Meet Local Hosts",
            "Responsible and Informed Travel",
            "What You Can Verify",
            "Begin planning your journey through Afghanistan.",
        )

        self.assertEqual(response.status_code, 200)
        positions = [page.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertContains(response, "Private and Small-Group Journeys in Afghanistan")
        self.assertContains(response, "Explore Our Tours")
        self.assertContains(response, "Plan a Private Journey")
        self.assertContains(
            response,
            "Travel conditions in Afghanistan can change. Larmoond provides local coordination, route review and contingency planning",
        )

    def test_only_complete_published_featured_tours_are_rendered(self):
        ready = self.create_tour()
        self.create_tour(available=False)
        self.create_tour(featured=False)
        self.create_tour(image="")
        stale = self.create_tour(
            type="schedule",
            start_date=timezone.localdate() - timedelta(days=4),
            end_date=timezone.localdate() - timedelta(days=1),
        )

        response = self.client.get(reverse("home:home"))

        self.assertEqual([item.tour for item in response.context["featured_tours"]], [ready])
        self.assertContains(response, ready.title)
        self.assertNotContains(response, stale.title)
        self.assertContains(response, "Kabul · Bamyan")
        self.assertContains(response, "Moderate")
        self.assertContains(response, "USD 640.00")

    def test_empty_tour_state_promotes_a_private_request_without_broken_grid(self):
        response = self.client.get(reverse("home:home"))

        self.assertContains(response, "Planning something private?")
        self.assertNotContains(response, 'class="lm-tour-grid"')

    def test_licence_claim_requires_badge_number_and_authority(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(
            show_licence_badge=True,
            licence_number="",
            licence_authority="",
        )
        response = self.client.get(reverse("home:home"))
        self.assertNotContains(response, "Licensed Afghan Travel Operator")

        Main_things.objects.filter(pk=self.configuration.pk).update(
            licence_number="LTT-2026-17",
            licence_authority="Verified tourism authority",
        )
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "Licensed Afghan Travel Operator")

    def test_hosting_promise_lists_only_enabled_services(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(
            enabled_hosting_services=["trip_consultation", "route_review"]
        )

        response = self.client.get(reverse("home:home"))

        self.assertContains(response, "Trip consultation")
        self.assertContains(response, "Route review")
        self.assertNotContains(response, "Visa guidance")
        self.assertNotContains(response, "Airport welcome when included")

    def test_destinations_are_complete_local_records_capped_at_eight(self):
        for index in range(9):
            PopularPlace.objects.create(
                title=f"Destination {index}",
                province="Bamyan",
                description=f"Accurate destination summary {index}.",
                static_image="image_for_province/bamyan.webp",
                url_name="states:bamyan",
                display_order=index,
                is_active=True,
            )
        PopularPlace.objects.create(
            title="Missing image destination",
            province="Kabul",
            description="This record has no approved image.",
            static_image="",
            display_order=20,
            is_active=True,
        )

        response = self.client.get(reverse("home:home"))

        self.assertEqual(len(response.context["destinations"]), 8)
        self.assertContains(response, 'loading="lazy"')
        self.assertContains(response, 'alt="Destination 0 in Bamyan"')
        self.assertNotContains(response, "Destination 8")
        self.assertNotContains(response, "Missing image destination")

    def test_only_approved_active_hosts_render_and_private_fields_never_do(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(
            show_team_section=True
        )
        self.create_public_host()
        TourGuide.objects.create(
            name="Unapproved Applicant",
            phone="PRIVATE-PHONE-888",
            email="applicant@example.test",
            provinces="Herat",
            languages="Dari",
            experience_years=2,
            specialties=["cultural"],
            bio="This application must not render.",
            id_number="PRIVATE-ID-888",
            profile_image="guides/applicant.webp",
            is_approved=False,
            is_active=True,
        )

        response = self.client.get(reverse("home:home"))

        self.assertContains(response, "Approved Host")
        self.assertContains(response, "A public professional biography")
        self.assertNotContains(response, "Unapproved Applicant")
        self.assertNotContains(response, "PRIVATE-PHONE-777")
        self.assertNotContains(response, "PRIVATE-ID-777")
        self.assertNotContains(response, "private-record.pdf")
        self.assertNotContains(response, "private-guide@example.test")

    def test_reviews_require_public_consent_and_a_completed_customer_booking(self):
        Main_things.objects.filter(pk=self.configuration.pk).update(show_reviews=True)
        tour = self.create_tour(featured=False)
        traveller = User.objects.create_user(
            username="completed-traveller",
            email="completed@example.test",
            password="test-pass",
            my_choice_field="Tourist",
        )
        crew_user = User.objects.create_user(
            username="reviewed-guide",
            email="guide-review@example.test",
            password="test-pass",
            my_choice_field="Guide",
        )
        role = CrewRole.objects.create(code="homepage-guide", name="Homepage guide")
        crew = CrewMember.objects.create(
            user=crew_user,
            display_name="Reviewed Guide",
            phone="0700000000",
            base_location="Bamyan",
            verification_status="approved",
        )
        Booking.objects.create(
            tour=tour,
            user=traveller,
            booking_date=timezone.localdate(),
            name="Completed Traveller",
            email="completed@example.test",
            phone="0700000001",
            situation="completed",
            paid=True,
            paid_amount=640,
        )
        engagement = CrewEngagement.objects.create(
            tour=tour,
            crew=crew,
            role=role,
            start_at=timezone.now() - timedelta(days=3),
            end_at=timezone.now() - timedelta(days=1),
            agreed_amount=Decimal("100.00"),
            status="completed",
        )
        review = CrewReview.objects.create(
            engagement=engagement,
            reviewer=traveller,
            reviewer_type="tourist",
            professionalism=5,
            knowledge=5,
            communication=5,
            punctuality=5,
            safety=5,
            overall=5,
            comment="A verified completed-journey review.",
            is_public=False,
        )

        response = self.client.get(reverse("home:home"))
        self.assertNotContains(response, review.comment)
        self.assertContains(response, "What You Can Verify")

        review.is_public = True
        review.save(update_fields=("is_public",))
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, review.comment)
        self.assertContains(response, "Feedback from completed journeys")
        self.assertNotContains(response, "What You Can Verify")


class HomepageLaunchReadinessTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()
        configuration = Main_things.objects.create(
            hero_description="Launch readiness configuration",
            active_public_languages=["en"],
        )
        Main_things.objects.filter(pk=configuration.pk).update(
            legal_entity_name="Verified legal entity",
            operating_company_name="Verified operating company",
            office_address="Verified office address",
            office_city="Kabul",
            office_country="Afghanistan",
            primary_email="public@larmoond.example",
            primary_phone="+93700111222",
            primary_domain="larmoond.example",
            logo_primary="brand/logos/primary.svg",
            logo_reversed="brand/logos/reversed.svg",
            logo_symbol="brand/icons/symbol.svg",
            favicon="brand/icons/favicon.ico",
            default_social_image="brand/social/default.webp",
            minimum_featured_tours_for_launch=1,
        )
        self.category = TourCategory.objects.create(
            name="Readiness tours",
            slug="readiness-tours",
            icon="ti ti-route",
        )

    def create_ready_tour(self):
        tour = Tour.objects.create(
            category=self.category,
            title="Launch-ready journey",
            image="tour-image/launch-ready.webp",
            slug="launch-ready-journey",
            type="not_schedule",
            description="Complete public journey.",
            location=["Bamyan"],
            duration_day="1",
            duration_night="0",
            price=Decimal("500.00"),
            available=True,
        )
        ItineraryItem.objects.create(
            tour=tour,
            day_number=1,
            title="Arrival",
            description="Complete day plan.",
            date=timezone.now(),
        )
        TourHomepageFeature.objects.create(
            tour=tour,
            physical_level="easy",
            is_active=True,
        )
        return tour

    def test_readiness_fails_until_required_featured_tours_are_published(self):
        stdout = StringIO()
        with self.assertRaises(CommandError):
            call_command("check_launch_readiness", stdout=stdout)

        self.assertIn("Complete published featured tours: 0/1", stdout.getvalue())

    def test_readiness_passes_when_public_settings_and_tour_threshold_are_ready(self):
        tour = self.create_ready_tour()
        self.assertEqual([item.tour for item in public_featured_tours()], [tour])
        stdout = StringIO()

        call_command("check_launch_readiness", stdout=stdout)

        self.assertIn("Site launch readiness passed", stdout.getvalue())


class HomepageAssetAndTranslationTests(TestCase):
    def test_homepage_styles_are_mobile_first_accessible_and_motion_aware(self):
        source = (
            Path(settings.BASE_DIR) / "static/css/larmoond-homepage.css"
        ).read_text(encoding="utf-8")

        self.assertIn(":focus-visible", source)
        self.assertIn("@media (min-width: 640px)", source)
        self.assertIn("@media (min-width: 900px)", source)
        self.assertIn("@media (prefers-reduced-motion: reduce)", source)
        self.assertIn("var(--brand-deep-green)", source)
        self.assertIn("var(--brand-lime)", source)

    def test_active_language_catalogs_translate_homepage_sales_messages(self):
        required_messages = (
            "Private and Small-Group Journeys in Afghanistan",
            "Afghanistan, hosted by those who call it home.",
            "More than a tour. Your local host in Afghanistan.",
            "Trip consultation",
            "Responsible and Informed Travel",
            "Begin planning your journey through Afghanistan.",
        )

        for language_code in ("fa", "ar"):
            catalog = (
                Path(settings.BASE_DIR)
                / f"home/locale/{language_code}/LC_MESSAGES/django.po"
            ).read_text(encoding="utf-8")
            for message in required_messages:
                with self.subTest(language_code=language_code, message=message):
                    entry_start = catalog.index(f'msgid "{message}"')
                    entry = catalog[entry_start : catalog.find("\n\n", entry_start)]
                    self.assertNotIn('msgstr ""', entry)
