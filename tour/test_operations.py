from datetime import timedelta
from decimal import Decimal

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, PickupPlan, Tour, TourCategory


User = get_user_model()


class OperationsCenterTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='ops-customer',
            email='customer@example.com',
            password='test-pass-123',
            my_choice_field='Tourist',
        )
        self.operator = User.objects.create_user(
            username='operator',
            email='operator@example.com',
            password='test-pass-123',
            my_choice_field='Operator',
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='test-pass-123',
            my_choice_field='Moderator',
        )
        self.superuser = User.objects.create_superuser(
            username='root-operator',
            email='root@example.com',
            password='test-pass-123',
        )
        self.category = TourCategory.objects.create(
            name='Operations Cultural',
            slug='operations-cultural',
            icon='ti ti-route',
        )
        self.tour = Tour.objects.create(
            category=self.category,
            title='Operations Bamyan Tour',
            image='tour-image/operations.jpg',
            slug='operations-bamyan-tour',
            type='schedule',
            start_date=timezone.localdate() + timedelta(days=10),
            end_date=timezone.localdate() + timedelta(days=14),
            description='Operational test tour.',
            location='Bamyan',
            duration_day='5',
            duration_night='4',
            price=Decimal('250.00'),
            available=True,
            google_location='https://maps.example.test/bamyan',
        )
        self.booking = Booking.objects.create(
            tour=self.tour,
            user=self.customer,
            booking_date=timezone.localdate() + timedelta(days=10),
            name='Operations Customer',
            email='customer@example.com',
            phone='+93700000000',
            situation='Booked',
            adults=2,
            children=1,
            paid=False,
            paid_amount=750,
        )

    def test_customer_is_blocked_from_operations_center(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('tour:operations:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_operator_role_can_open_live_dashboard(self):
        self.client.force_login(self.operator)
        response = self.client.get(reverse('tour:operations:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['new_requests'], 1)
        self.assertContains(response, self.booking.name)

    def test_operations_dashboard_uses_standalone_management_shell(self):
        self.client.force_login(self.operator)
        response = self.client.get(reverse('tour:operations:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-operations-shell')
        self.assertContains(response, 'operations-shell.js')
        self.assertContains(response, 'Secure management workspace')
        self.assertNotContains(response, 'class="aa-site-header"')
        self.assertNotContains(response, 'Become an Expert')
        self.assertNotContains(response, 'Plan Your Trip')

    def test_content_navigation_is_only_visible_to_authorized_roles(self):
        self.client.force_login(self.operator)
        operator_response = self.client.get(reverse('tour:operations:dashboard'))
        self.assertNotContains(operator_response, 'Tours & categories')
        self.assertNotContains(operator_response, 'Media library')

        self.client.force_login(self.moderator)
        moderator_response = self.client.get(reverse('tour:operations:dashboard'))
        self.assertContains(moderator_response, 'Tours & categories')
        self.assertContains(moderator_response, 'Media library')
        self.assertContains(
            moderator_response,
            reverse('tour:operations:content_tour_list'),
        )

    def test_dashboard_router_sends_operator_to_operations(self):
        self.client.force_login(self.operator)
        response = self.client.get(reverse('tour:dashboard'))
        self.assertRedirects(
            response,
            reverse('tour:operations:dashboard'),
            fetch_redirect_response=False,
        )

    def test_unpaid_booking_cannot_enter_upcoming_stage(self):
        self.client.force_login(self.operator)
        response = self.client.post(
            reverse('tour:operations:booking_update_status', args=[self.booking.id]),
            {'situation': 'upcoming', 'reason': ''},
        )
        self.booking.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('tour:operations:booking_detail', args=[self.booking.id]),
        )
        self.assertEqual(self.booking.situation, 'Booked')

    def test_paid_booking_transition_is_saved_and_audited(self):
        self.booking.paid = True
        self.booking.save(update_fields=['paid'])
        self.client.force_login(self.operator)
        response = self.client.post(
            reverse('tour:operations:booking_update_status', args=[self.booking.id]),
            {'situation': 'upcoming', 'reason': 'Payment verified.'},
        )
        self.booking.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('tour:operations:booking_detail', args=[self.booking.id]),
        )
        self.assertEqual(self.booking.situation, 'upcoming')
        self.assertTrue(
            LogEntry.objects.filter(
                object_id=str(self.booking.id),
                change_message__icontains='Status changed',
            ).exists()
        )

    def test_only_moderator_or_superuser_can_record_offline_payment(self):
        url = reverse('tour:operations:booking_record_payment', args=[self.booking.id])
        payload = {
            'amount': 750,
            'reference': 'BANK-1001',
            'reason': 'Verified bank transfer.',
        }

        self.client.force_login(self.operator)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.moderator)
        response = self.client.post(url, payload)
        self.booking.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('tour:operations:booking_detail', args=[self.booking.id]),
        )
        self.assertTrue(self.booking.paid)
        self.assertEqual(self.booking.situation, 'upcoming')
        self.assertIn('BANK-1001', self.booking.notes)

    def test_pickup_plan_is_created_and_status_persisted(self):
        self.booking.paid = True
        self.booking.situation = 'upcoming'
        self.booking.save(update_fields=['paid', 'situation'])
        self.client.force_login(self.operator)
        response = self.client.post(
            reverse('tour:operations:booking_pickup', args=[self.booking.id]),
            {
                'pickup_type': 'airport',
                'entry_point_label': 'Kabul International Airport',
                'entry_point_code': 'kabul_airport',
                'scheduled_at': (timezone.now() + timedelta(days=9)).strftime('%Y-%m-%dT%H:%M'),
                'window_minutes': 60,
                'tourist_phone_share': self.booking.phone,
                'meeting_point': 'Arrival Gate A',
                'visible_to_tourist': 'on',
                'status': 'waiting',
                'otp_code': '1842',
            },
        )
        self.assertRedirects(
            response,
            reverse('tour:operations:booking_detail', args=[self.booking.id]),
        )
        pickup = PickupPlan.objects.get(booking=self.booking)
        self.assertEqual(pickup.status, 'waiting')
        self.assertEqual(pickup.meeting_point, 'Arrival Gate A')

    def test_tour_operations_update_availability_and_dates(self):
        self.client.force_login(self.operator)
        new_start = timezone.localdate() + timedelta(days=30)
        new_end = new_start + timedelta(days=4)
        response = self.client.post(
            reverse('tour:operations:tour_detail', args=[self.tour.id]),
            {
                'start_date': new_start.isoformat(),
                'end_date': new_end.isoformat(),
            },
        )
        self.tour.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('tour:operations:tour_detail', args=[self.tour.id]),
        )
        self.assertFalse(self.tour.available)
        self.assertEqual(self.tour.start_date, new_start)

    def test_booking_export_is_staff_only_csv(self):
        self.client.force_login(self.operator)
        response = self.client.get(reverse('tour:operations:booking_export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Operations Customer', response.content.decode())
