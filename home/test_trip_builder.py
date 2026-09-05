from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tour.models import Booking, Tour, TourCategory

from .models import (
    EntryPlan,
    PopularPlace,
    RouteProposal,
    RouteProposalDay,
    TripPreference,
    TripRequest,
    TripStop,
)


User = get_user_model()


class TripBuilderFlowTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="route-customer",
            email="route-customer@example.com",
            password="test-pass-123",
            my_choice_field="Tourist",
        )
        self.other_customer = User.objects.create_user(
            username="other-route-customer",
            email="other-route@example.com",
            password="test-pass-123",
            my_choice_field="Tourist",
        )
        self.operator = User.objects.create_user(
            username="route-operator",
            email="route-operator@example.com",
            password="test-pass-123",
            my_choice_field="Operator",
        )
        self.kabul = PopularPlace.objects.create(
            title="Kabul",
            province="Kabul",
            description="Kabul destination",
            static_image="image_for_province/kabul.jpeg",
            url_name="states:kabul",
            is_active=True,
        )
        self.bamyan = PopularPlace.objects.create(
            title="Bamyan",
            province="Bamyan",
            description="Bamyan destination",
            static_image="image_for_province/bamyan2.jpg",
            url_name="states:bamyan",
            is_active=True,
        )
        self.start_date = timezone.localdate() + timedelta(days=30)

    def _payload(self):
        return {
            "trip-full_name": "Route Customer",
            "trip-email": self.customer.email,
            "trip-phone": "+93700111222",
            "trip-country_of_origin": "Germany",
            "trip-start_date": self.start_date.isoformat(),
            "trip-end_date": (self.start_date + timedelta(days=7)).isoformat(),
            "trip-adults": "2",
            "trip-children": "1",
            "trip-budget_tier": "comfort",
            "trip-estimated_budget": "1800",
            "trip-pace": "balanced",
            "trip-notes": "Focus on culture.",
            "entry-selection_mode": "recommend",
            "entry-transport_mode": "either",
            "entry-arrival_origin": "Frankfurt",
            "entry-selected_entry_point": "",
            "entry-other_entry_point": "",
            "preferences-interests": ["culture", "history"],
            "preferences-accommodation_type": "hotel",
            "preferences-transport_preference": "private",
            "preferences-needs_local_guide": "on",
            "preferences-accessibility_notes": "",
            "stops-TOTAL_FORMS": "2",
            "stops-INITIAL_FORMS": "0",
            "stops-MIN_NUM_FORMS": "1",
            "stops-MAX_NUM_FORMS": "12",
            "stops-0-position": "1",
            "stops-0-destination": str(self.kabul.pk),
            "stops-0-nights": "2",
            "stops-0-notes": "Arrival and city orientation",
            "stops-1-position": "2",
            "stops-1-destination": str(self.bamyan.pk),
            "stops-1-nights": "3",
            "stops-1-notes": "Band-e Amir",
        }

    def _submit_request(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse("home:trip_builder"), self._payload())
        trip_request = TripRequest.objects.get(email=self.customer.email)
        return response, trip_request

    def test_home_route_form_opens_real_trip_builder(self):
        response = self.client.get(reverse("home:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("home:trip_builder"))

        builder = self.client.get(
            reverse("home:trip_builder"),
            {"q": "Bamyan", "guests": "3", "check_in": self.start_date.isoformat()},
        )
        self.assertEqual(builder.status_code, 200)
        self.assertContains(builder, "Build a journey across several provinces")
        self.assertContains(builder, 'value="3"')

    def test_submission_saves_request_stops_entry_and_preferences(self):
        response, trip_request = self._submit_request()

        self.assertRedirects(response, trip_request.get_absolute_url())
        self.assertEqual(trip_request.user_id, self.customer.pk)
        self.assertEqual(trip_request.status, "submitted")
        self.assertEqual(trip_request.traveller_count, 3)
        self.assertEqual(
            list(trip_request.stops.values_list("destination__title", flat=True)),
            ["Kabul", "Bamyan"],
        )
        self.assertEqual(trip_request.entry_plan.selection_mode, "recommend")
        self.assertEqual(trip_request.entry_plan.status, "pending")
        self.assertEqual(trip_request.preferences.interests, ["culture", "history"])
        requests_page = self.client.get(reverse("home:my_trip_requests"))
        self.assertEqual(requests_page.status_code, 200)
        self.assertContains(requests_page, trip_request.reference)

    def test_duplicate_province_is_rejected(self):
        payload = self._payload()
        payload["stops-1-destination"] = str(self.kabul.pk)
        self.client.force_login(self.customer)
        response = self.client.post(reverse("home:trip_builder"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Each province can appear only once")
        self.assertFalse(TripRequest.objects.exists())

    def test_route_request_detail_is_private(self):
        _, trip_request = self._submit_request()
        self.client.force_login(self.other_customer)
        response = self.client.get(trip_request.get_absolute_url())
        self.assertEqual(response.status_code, 403)

    def test_proposal_acceptance_and_booking_conversion(self):
        _, trip_request = self._submit_request()
        proposal = RouteProposal.objects.create(
            trip_request=trip_request,
            version=1,
            title="Kabul and Bamyan route",
            summary="A reviewed cultural route.",
            proposed_entry_point="Kabul International Airport",
            total_price=Decimal("1500.00"),
            currency="USD",
            customer_message="Please review this route.",
            status="draft",
            created_by_id=self.operator.pk,
        )
        RouteProposalDay.objects.create(
            proposal=proposal,
            day_number=1,
            destination=self.kabul,
            title="Arrival in Kabul",
            description="Airport pickup and city orientation.",
            overnight_location="Kabul",
            transport="Private vehicle",
        )

        self.client.force_login(self.operator)
        list_response = self.client.get(reverse("tour:operations:trip_request_list"))
        detail_response = self.client.get(
            reverse("tour:operations:trip_request_detail", args=[trip_request.pk])
        )
        proposal_form_response = self.client.get(
            reverse("tour:operations:trip_proposal_create", args=[trip_request.pk])
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(proposal_form_response.status_code, 200)
        self.assertContains(proposal_form_response, "Kabul · day 1")

        send_response = self.client.post(
            reverse(
                "tour:operations:trip_proposal_send",
                args=[trip_request.pk, proposal.pk],
            )
        )
        self.assertRedirects(
            send_response,
            reverse("tour:operations:trip_request_detail", args=[trip_request.pk]),
        )
        proposal.refresh_from_db()
        trip_request.refresh_from_db()
        self.assertEqual(proposal.status, "sent")
        self.assertEqual(trip_request.status, "proposal_sent")

        self.client.force_login(self.customer)
        accept_response = self.client.post(
            reverse("home:trip_request_action", args=[trip_request.public_id]),
            {"action": "accept", "proposal_id": proposal.pk},
        )
        self.assertRedirects(accept_response, trip_request.get_absolute_url())
        proposal.refresh_from_db()
        trip_request.refresh_from_db()
        self.assertEqual(proposal.status, "accepted")
        self.assertEqual(trip_request.status, "approved")

        category = TourCategory.objects.create(
            name="Custom routes",
            slug="custom-routes",
            icon="ti ti-route",
        )
        tour = Tour.objects.create(
            category=category,
            title="Kabul and Bamyan custom route",
            image="tour-image/custom-route.jpg",
            slug="kabul-bamyan-custom-route",
            type="schedule",
            start_date=trip_request.start_date,
            end_date=trip_request.end_date,
            description="Custom route prepared by operations.",
            location=["Kabul", "Bamyan"],
            duration_day="8",
            duration_night="7",
            price=proposal.total_price,
            available=True,
            google_location="https://maps.example.test/custom-route",
        )
        proposal.booking_tour_id = tour.pk
        proposal.save(update_fields=("booking_tour_id",))

        self.client.force_login(self.operator)
        conversion = self.client.post(
            reverse(
                "tour:operations:trip_request_convert_booking",
                args=[trip_request.pk],
            )
        )
        trip_request.refresh_from_db()
        self.assertEqual(conversion.status_code, 302)
        self.assertEqual(trip_request.status, "booked")
        booking = Booking.objects.get(pk=trip_request.booking_id)
        self.assertEqual(booking.user, self.customer)
        self.assertEqual(booking.tour, tour)
        self.assertEqual(booking.paid_amount, 1500)

    def test_operator_can_save_generated_day_by_day_proposal(self):
        _, trip_request = self._submit_request()
        self.client.force_login(self.operator)
        response = self.client.post(
            reverse("tour:operations:trip_proposal_create", args=[trip_request.pk]),
            {
                "title": "Reviewed multi-province plan",
                "summary": "A practical route prepared by operations.",
                "proposed_entry_point": "Kabul International Airport",
                "total_price": "1750.00",
                "currency": "USD",
                "valid_until": (timezone.localdate() + timedelta(days=14)).isoformat(),
                "customer_message": "Review the daily plan below.",
                "internal_notes": "Confirm transport before sending.",
                "booking_tour": "",
                "days-TOTAL_FORMS": "2",
                "days-INITIAL_FORMS": "0",
                "days-MIN_NUM_FORMS": "1",
                "days-MAX_NUM_FORMS": "1000",
                "days-0-day_number": "1",
                "days-0-destination": str(self.kabul.pk),
                "days-0-title": "Kabul arrival",
                "days-0-description": "Pickup and orientation.",
                "days-0-transport": "Private vehicle",
                "days-0-overnight_location": "Kabul",
                "days-1-day_number": "2",
                "days-1-destination": str(self.bamyan.pk),
                "days-1-title": "Transfer to Bamyan",
                "days-1-description": "Overland transfer and local visit.",
                "days-1-transport": "Private vehicle",
                "days-1-overnight_location": "Bamyan",
            },
        )
        self.assertRedirects(
            response,
            reverse("tour:operations:trip_request_detail", args=[trip_request.pk]),
        )
        proposal = RouteProposal.objects.get(trip_request=trip_request)
        self.assertEqual(proposal.status, "draft")
        self.assertEqual(proposal.days.count(), 2)
        self.assertEqual(
            list(proposal.days.values_list("day_number", flat=True)),
            [1, 2],
        )
