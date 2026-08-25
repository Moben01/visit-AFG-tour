from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, Languages, Tour, TourCategory


User = get_user_model()


class CustomerPortalTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='test-pass-123',
            my_choice_field='Tourist',
        )
        self.other_customer = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='test-pass-123',
            my_choice_field='Tourist',
        )
        self.guide = User.objects.create_user(
            username='guide',
            email='guide@example.com',
            password='test-pass-123',
            my_choice_field='Guide',
        )
        self.staff = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='test-pass-123',
            is_staff=True,
            my_choice_field='Operator',
        )
        self.category = TourCategory.objects.create(
            name='Cultural',
            slug='cultural',
            icon='ti ti-building',
        )
        self.tour = Tour.objects.create(
            category=self.category,
            title='Bamyan Discovery',
            image='tour-image/test.jpg',
            slug='bamyan-discovery',
            type='schedule',
            start_date=timezone.localdate() + timedelta(days=20),
            end_date=timezone.localdate() + timedelta(days=24),
            description='A cultural journey.',
            location='Bamyan',
            duration_day='5',
            duration_night='4',
            price=Decimal('100.00'),
            available=True,
            google_location='https://maps.example.test/bamyan',
        )

    def _booking(self, user=None, **overrides):
        values = {
            'tour': self.tour,
            'user': user or self.customer,
            'booking_date': timezone.localdate() + timedelta(days=20),
            'name': 'Test Customer',
            'email': 'customer@example.com',
            'phone': '+93700000000',
            'situation': 'Booked',
            'adults': 1,
            'children': 0,
            'paid': False,
            'paid_amount': 100,
        }
        values.update(overrides)
        return Booking.objects.create(**values)

    def test_dashboard_router_sends_each_role_to_its_portal(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('tour:dashboard'))
        self.assertRedirects(response, reverse('tour:customer_dashboard'))

        self.client.force_login(self.guide)
        response = self.client.get(reverse('tour:dashboard'))
        self.assertRedirects(response, reverse('tour:user_newsfeed'))

        self.client.force_login(self.staff)
        response = self.client.get(reverse('tour:dashboard'))
        self.assertRedirects(response, reverse('tour:operations:dashboard'))

    def test_customer_dashboard_contains_only_owners_bookings(self):
        own_booking = self._booking()
        other_tour = Tour.objects.create(
            category=self.category,
            title='Private Other Tour',
            image='tour-image/other.jpg',
            slug='private-other-tour',
            type='schedule',
            start_date=timezone.localdate() + timedelta(days=30),
            end_date=timezone.localdate() + timedelta(days=32),
            description='Not visible to the first customer.',
            location='Herat',
            duration_day='3',
            duration_night='2',
            price=Decimal('200.00'),
            available=True,
            google_location='https://maps.example.test/herat',
        )
        self._booking(user=self.other_customer, tour=other_tour)

        self.client.force_login(self.customer)
        response = self.client.get(reverse('tour:customer_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, own_booking.tour.title)
        self.assertNotContains(response, other_tour.title)
        self.assertEqual(response.context['total_bookings'], 1)

    def test_booking_creates_server_priced_pending_record(self):
        Languages.objects.create(name='English', code='en', total_price=25)
        self.client.force_login(self.customer)
        response = self.client.post(
            reverse('tour:tour_booking', args=[self.tour.slug]),
            {
                'name': 'Customer Name',
                'email': 'customer@example.com',
                'phone': '+93700111222',
                'booking_date': (timezone.localdate() + timedelta(days=20)).isoformat(),
                'adults': 2,
                'children': 1,
                'notes': 'Vegetarian meals',
                'languages': ['en'],
            },
        )

        self.assertEqual(
            response.status_code, 302, str(response.context or response.content),
        )
        booking = Booking.objects.get(user=self.customer)
        self.assertRedirects(response, reverse('tour:payment', args=[booking.id]))
        self.assertEqual(booking.paid_amount, 325)
        self.assertFalse(booking.paid)
        self.assertEqual(booking.situation, 'Booked')
        self.assertIn('Translation languages: English', booking.notes)

    def test_my_trips_status_filter_uses_current_customer_only(self):
        self._booking(situation='upcoming', paid=True)
        self._booking(situation='completed', paid=True)
        self._booking(user=self.other_customer, situation='upcoming', paid=True)
        self.client.force_login(self.customer)

        response = self.client.get(reverse('tour:customer_tours'), {'status': 'upcoming'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['upcomming_tours']), 1)
        self.assertEqual(response.context['upcomming_tours'][0].user, self.customer)
        self.assertEqual(response.context['upcomming_tours'][0].situation, 'upcoming')

    def test_customer_cannot_open_another_customers_payment(self):
        other_booking = self._booking(user=self.other_customer)
        self.client.force_login(self.customer)

        response = self.client.get(reverse('tour:payment', args=[other_booking.id]))

        self.assertEqual(response.status_code, 404)

    def test_customer_cannot_view_another_customers_pickup(self):
        other_booking = self._booking(user=self.other_customer, paid=True, situation='upcoming')
        self.client.force_login(self.customer)

        response = self.client.get(reverse('tour:pickup_plan_detail', args=[other_booking.id]))

        self.assertEqual(response.status_code, 403)

    def test_unpaid_booking_redirects_to_payment_before_trip_management(self):
        booking = self._booking()
        self.client.force_login(self.customer)

        response = self.client.get(reverse('tour:up_commoing_tours_more_info', args=[booking.id]))

        self.assertRedirects(response, reverse('tour:payment', args=[booking.id]))

    @patch('tour.views.stripe.checkout.Session.create')
    def test_checkout_uses_server_amount_and_booking_metadata(self, create_session):
        booking = self._booking(paid_amount=275)
        create_session.return_value.url = 'https://checkout.stripe.test/session'
        self.client.force_login(self.customer)

        response = self.client.post(reverse('tour:create_checkout_session', args=[booking.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://checkout.stripe.test/session')
        kwargs = create_session.call_args.kwargs
        self.assertEqual(kwargs['line_items'][0]['price_data']['unit_amount'], 27500)
        self.assertEqual(kwargs['metadata']['booking_id'], str(booking.id))
        self.assertEqual(kwargs['metadata']['user_id'], str(self.customer.id))
