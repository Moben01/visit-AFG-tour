from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from home.models import TourHomepageFeature

from .models import ItineraryItem, Tour, TourCategory


User = get_user_model()


class TourContentManagementTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            username="tour-content-moderator",
            email="tour-content-moderator@example.com",
            password="test-pass-123",
            my_choice_field="Moderator",
        )
        self.customer = User.objects.create_user(
            username="tour-content-customer",
            email="tour-content-customer@example.com",
            password="test-pass-123",
            my_choice_field="Tourist",
        )
        self.category = TourCategory.objects.create(
            name="Cultural",
            slug="content-cultural",
            icon="ti ti-route",
        )
        self.client.force_login(self.moderator)

    def create_tour(self, **overrides):
        values = {
            "category": self.category,
            "title": "Bamyan discovery",
            "image": "tour-image/bamyan.jpg",
            "slug": "bamyan-discovery",
            "type": "not_schedule",
            "description": "A practical cultural route through Bamyan.",
            "location": "Bamyan",
            "duration_day": "1",
            "duration_night": "0",
            "price": Decimal("125.00"),
            "available": False,
            "google_location": "",
        }
        values.update(overrides)
        return Tour.objects.create(**values)

    def tour_payload(self, tour, **overrides):
        values = {
            "category": str(self.category.pk),
            "title": tour.title,
            "type": tour.type,
            "description": tour.description,
            "start_date": tour.start_date.isoformat() if tour.start_date else "",
            "end_date": tour.end_date.isoformat() if tour.end_date else "",
            "duration_day": tour.duration_day,
            "duration_night": tour.duration_night,
            "location": ["Bamyan"],
            "price": str(tour.price),
            "google_location": tour.google_location,
        }
        values.update(overrides)
        return values

    def add_day(self, tour, day_number=1, title="Arrival"):
        return ItineraryItem.objects.create(
            tour=tour,
            day_number=day_number,
            title=title,
            description=f"Plan for day {day_number}.",
            date=timezone.now() + timedelta(days=day_number - 1),
            image="",
            type_of_transport="",
        )

    def test_minimal_tour_can_be_saved_as_private_draft(self):
        response = self.client.post(
            reverse("tour:operations:content_tour_create"),
            {
                "category": str(self.category.pk),
                "title": "Flexible Herat journey",
                "type": "not_schedule",
                "description": "A draft route that will be completed later.",
                "action": "draft",
            },
        )

        tour = Tour.objects.get(title="Flexible Herat journey")
        self.assertRedirects(
            response,
            reverse("tour:operations:content_tour_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(tour.available)
        self.assertTrue(tour.slug)
        self.assertFalse(bool(tour.image))
        self.assertEqual(tour.price, Decimal("0.00"))

    def test_itinerary_day_can_be_added_with_only_a_description(self):
        tour = self.create_tour()
        response = self.client.post(
            reverse("tour:operations:content_tour_itinerary_create", args=[tour.pk]),
            {"description": "Arrival, orientation and a short city walk."},
        )

        item = tour.itinerary_items.get()
        self.assertRedirects(
            response,
            f"{reverse('tour:operations:content_tour_edit', args=[tour.pk])}#itinerary",
            fetch_redirect_response=False,
        )
        self.assertEqual(item.day_number, 1)
        self.assertEqual(item.type_of_transport, "")
        self.assertFalse(bool(item.image))
        self.assertIsNotNone(item.date)

    def test_publish_is_blocked_until_an_itinerary_exists(self):
        tour = self.create_tour()
        response = self.client.post(
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            {**self.tour_payload(tour), "action": "publish"},
        )

        tour.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(tour.available)
        self.assertContains(response, "Add at least one itinerary day before publishing.")

    def test_complete_tour_can_be_published(self):
        tour = self.create_tour()
        self.add_day(tour)
        response = self.client.post(
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            {**self.tour_payload(tour), "action": "publish"},
        )

        tour.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            fetch_redirect_response=False,
        )
        self.assertTrue(tour.available)

    def test_published_tour_can_be_selected_for_homepage_with_physical_level(self):
        tour = self.create_tour()
        self.add_day(tour)

        response = self.client.post(
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            {
                **self.tour_payload(tour),
                "homepage_featured": "on",
                "homepage_physical_level": "moderate",
                "homepage_display_order": "2",
                "action": "publish",
            },
        )

        self.assertRedirects(
            response,
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            fetch_redirect_response=False,
        )
        feature = TourHomepageFeature.objects.get(tour=tour)
        self.assertTrue(feature.is_active)
        self.assertEqual(feature.physical_level, "moderate")
        self.assertEqual(feature.display_order, 2)

    def test_homepage_selection_requires_a_physical_level(self):
        tour = self.create_tour()
        self.add_day(tour)

        response = self.client.post(
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            {
                **self.tour_payload(tour),
                "homepage_featured": "on",
                "homepage_physical_level": "",
                "action": "publish",
            },
        )

        tour.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(tour.available)
        self.assertContains(response, "Select a physical level before featuring this tour.")
        self.assertFalse(TourHomepageFeature.objects.filter(tour=tour).exists())

    def test_save_changes_preserves_a_published_tour(self):
        tour = self.create_tour(available=True)
        self.add_day(tour)
        response = self.client.post(
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            {**self.tour_payload(tour), "description": "Updated public description.", "action": "continue"},
        )

        tour.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            fetch_redirect_response=False,
        )
        self.assertTrue(tour.available)
        self.assertEqual(tour.description, "Updated public description.")

    def test_scheduled_tour_needs_both_dates_before_publish(self):
        tour = self.create_tour(type="schedule")
        self.add_day(tour)
        response = self.client.post(
            reverse("tour:operations:content_tour_edit", args=[tour.pk]),
            {**self.tour_payload(tour), "type": "schedule", "start_date": "", "end_date": "", "action": "publish"},
        )

        tour.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(tour.available)
        self.assertContains(response, "A scheduled tour needs a start date.")
        self.assertContains(response, "A scheduled tour needs an end date.")

    def test_itinerary_order_is_saved_and_resequenced(self):
        tour = self.create_tour(duration_day="2", duration_night="1")
        day_one = self.add_day(tour, 1, "First")
        day_two = self.add_day(tour, 2, "Second")
        response = self.client.post(
            reverse("tour:operations:content_tour_itinerary_order", args=[tour.pk]),
            {"day_order": [str(day_two.pk), str(day_one.pk)]},
        )

        day_one.refresh_from_db()
        day_two.refresh_from_db()
        self.assertRedirects(
            response,
            f"{reverse('tour:operations:content_tour_edit', args=[tour.pk])}#itinerary",
            fetch_redirect_response=False,
        )
        self.assertEqual(day_two.day_number, 1)
        self.assertEqual(day_one.day_number, 2)

    def test_draft_is_hidden_publicly_but_available_to_authorized_preview(self):
        tour = self.create_tour()
        detail_url = reverse("tour:tour_details", args=[tour.slug])
        self.client.logout()
        self.assertEqual(self.client.get(detail_url).status_code, 404)

        self.client.force_login(self.moderator)
        self.assertEqual(self.client.get(f"{detail_url}?preview=1").status_code, 200)

    def test_price_on_request_tour_cannot_enter_zero_price_booking(self):
        tour = self.create_tour(price=Decimal("0.00"), available=True)
        self.client.force_login(self.customer)
        response = self.client.get(reverse("tour:tour_booking", args=[tour.slug]))
        self.assertRedirects(
            response,
            f"{reverse('tour:tour_details', args=[tour.slug])}#enquires-content",
            fetch_redirect_response=False,
        )

    def test_itinerary_editor_renders_for_an_existing_tour(self):
        tour = self.create_tour()
        response = self.client.get(
            reverse("tour:operations:content_tour_itinerary_create", args=[tour.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Services and logistics")
        self.assertContains(response, "Save itinerary day")
