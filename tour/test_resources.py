from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Booking, CrewApplication, CrewEngagement, CrewMember, CrewOffer,
    CrewOpportunity, CrewPayment, CrewQualification, CrewReview, CrewRole,
    RequestForQuote, ServiceOrder, ServiceRequirement, ServiceSupplier,
    SupplierCategory, SupplierQuote, Tour, TourCategory,
)

User = get_user_model()


class ResourceFlowTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.category = TourCategory.objects.create(
            name='Cultural', slug='cultural-resource-tests', icon='ti-map', description='Test'
        )
        self.tour = Tour.objects.create(
            category=self.category, title='Bamyan Field Tour', image='tour-image/test.jpg',
            slug='bamyan-field-tour-resource-tests', type='schedule',
            start_date=(self.now + timedelta(days=10)).date(),
            end_date=(self.now + timedelta(days=15)).date(),
            description='Test tour', location=['Bamyan'], duration_day='5', duration_night='4',
            price=Decimal('800.00'), available=True, google_location='Bamyan',
        )
        self.moderator = User.objects.create_user(
            username='resource-moderator', email='resource-moderator@example.com',
            password='pass1234', my_choice_field='Moderator'
        )
        self.operator = User.objects.create_user(
            username='resource-operator', email='resource-operator@example.com',
            password='pass1234', my_choice_field='Operator'
        )
        self.crew_user = User.objects.create_user(
            username='field-guide', email='field-guide@example.com',
            password='pass1234', my_choice_field='Guide'
        )
        self.role = CrewRole.objects.create(code='test-guide', name='Test Tour Guide')
        self.crew = CrewMember.objects.create(
            user=self.crew_user, display_name='Field Guide', phone='0700000000',
            email='guide@example.com', base_location='Bamyan', languages='Dari, English',
            verification_status='approved', available_for_work=True,
        )
        CrewQualification.objects.create(
            crew=self.crew, role=self.role, experience_years=5, is_verified=True
        )
        self.opportunity = CrewOpportunity.objects.create(
            tour=self.tour, role=self.role, title='Guide for Bamyan', summary='Guide the group.',
            duties='Daily guiding', requirements='English', location='Bamyan',
            start_at=self.now + timedelta(days=10), end_at=self.now + timedelta(days=15),
            positions=1, minimum_experience_years=2, compensation_type='fixed',
            currency='USD', budget_min=Decimal('400'), budget_max=Decimal('500'),
            application_deadline=self.now + timedelta(days=5), status='published',
            created_by=self.moderator, published_at=self.now,
        )

    def _application_and_offer(self, opportunity=None, amount='475.00'):
        opportunity = opportunity or self.opportunity
        application = CrewApplication.objects.create(
            opportunity=opportunity, crew=self.crew, message='Available and interested.',
            proposed_amount=Decimal(amount), availability_confirmed=True,
            terms_acknowledged=True, status='offer_sent',
        )
        offer = CrewOffer.objects.create(
            application=application, version=1, compensation_type='fixed',
            amount=Decimal(amount), currency='USD', start_at=opportunity.start_at,
            end_at=opportunity.end_at, terms='Confirmed duties', status='sent',
            expires_at=self.now + timedelta(days=2), sent_by=self.moderator,
        )
        return application, offer

    def test_crew_can_apply_when_verified_and_available(self):
        self.client.force_login(self.crew_user)
        response = self.client.post(reverse('tour:crew:apply', args=[self.opportunity.pk]), {
            'message': 'I can support this tour.', 'relevant_experience': 'Five years.',
            'proposed_amount': '450.00', 'currency': 'USD',
            'availability_confirmed': 'on', 'terms_acknowledged': 'on',
        })
        self.assertRedirects(response, reverse('tour:crew:applications'))
        self.assertTrue(CrewApplication.objects.filter(opportunity=self.opportunity, crew=self.crew).exists())

    def test_accepting_offer_creates_dated_engagement(self):
        application, offer = self._application_and_offer()
        self.client.force_login(self.crew_user)
        response = self.client.post(reverse('tour:crew:offer_response', args=[offer.pk]), {'action': 'accept'})
        engagement = CrewEngagement.objects.get(application=application)
        self.assertRedirects(response, reverse('tour:crew:engagement_detail', args=[engagement.pk]))
        self.assertEqual(engagement.status, 'confirmed')
        self.assertEqual(engagement.agreed_amount, Decimal('475.00'))
        offer.refresh_from_db()
        self.assertEqual(offer.status, 'accepted')

    def test_overlapping_assignment_is_rejected(self):
        first_application, first_offer = self._application_and_offer()
        self.client.force_login(self.crew_user)
        self.client.post(reverse('tour:crew:offer_response', args=[first_offer.pk]), {'action': 'accept'})
        second = CrewOpportunity.objects.create(
            tour=self.tour, role=self.role, title='Overlapping guide role', summary='Overlap',
            location='Bamyan', start_at=self.now + timedelta(days=12),
            end_at=self.now + timedelta(days=14), positions=1,
            application_deadline=self.now + timedelta(days=4), status='published',
        )
        second_application, second_offer = self._application_and_offer(second)
        response = self.client.post(reverse('tour:crew:offer_response', args=[second_offer.pk]), {'action': 'accept'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CrewEngagement.objects.filter(application=second_application).exists())

    def test_supplier_quote_award_creates_service_order(self):
        supplier_user = User.objects.create_user(
            username='hotel-user', email='hotel-user@example.com', password='pass1234'
        )
        hotel = SupplierCategory.objects.create(code='test-hotel', name='Test Hotel')
        supplier = ServiceSupplier.objects.create(
            user=supplier_user, legal_name='Bamyan Hotel LLC', entity_type='company',
            contact_name='Hotel Manager', phone='0711111111', status='active',
        )
        supplier.categories.add(hotel)
        requirement = ServiceRequirement.objects.create(
            tour=self.tour, category=hotel, title='Ten hotel rooms', description='Ten twin rooms.',
            quantity=Decimal('10'), unit='room-night', location='Bamyan',
            start_at=self.now + timedelta(days=10), end_at=self.now + timedelta(days=15),
            needed_by=self.now + timedelta(days=5), status='sourcing', created_by=self.moderator,
        )
        rfq = RequestForQuote.objects.create(
            requirement=requirement, reference='RFQ-TEST-1', deadline=self.now + timedelta(days=4),
            status='published', created_by=self.moderator, published_at=self.now,
        )
        self.client.force_login(supplier_user)
        response = self.client.post(reverse('tour:supplier:rfq_detail', args=[rfq.pk]), {
            'amount': '1500.00', 'currency': 'USD', 'details': 'Ten rooms with breakfast.',
            'valid_until': (self.now + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertEqual(response.status_code, 302)
        quote = SupplierQuote.objects.get(rfq=rfq, supplier=supplier)
        self.client.force_login(self.moderator)
        response = self.client.post(reverse('tour:operations:quote_select', args=[quote.pk]))
        order = ServiceOrder.objects.get(quote=quote)
        self.assertRedirects(response, reverse('tour:operations:service_order_detail', args=[order.pk]))
        self.assertEqual(order.total_amount, Decimal('1500.00'))

    def test_only_finance_authority_can_record_crew_payment(self):
        application, offer = self._application_and_offer()
        engagement = CrewEngagement.objects.create(
            tour=self.tour, opportunity=self.opportunity, application=application, offer=offer,
            crew=self.crew, role=self.role, start_at=offer.start_at, end_at=offer.end_at,
            agreed_amount=offer.amount, status='completed',
        )
        payload = {
            'payment-base_amount': '475.00', 'payment-bonus_amount': '0',
            'payment-approved_expenses': '0', 'payment-deductions': '0',
            'payment-currency': 'USD', 'payment-status': 'paid',
        }
        self.client.force_login(self.operator)
        response = self.client.post(reverse('tour:operations:engagement_payment', args=[engagement.pk]), payload)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CrewPayment.objects.filter(engagement=engagement).exists())
        self.client.force_login(self.moderator)
        response = self.client.post(reverse('tour:operations:engagement_payment', args=[engagement.pk]), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CrewPayment.objects.get(engagement=engagement).status, 'paid')

    def test_only_customer_on_completed_tour_can_rate_assigned_crew(self):
        customer = User.objects.create_user(
            username='tour-customer', email='tour-customer@example.com', password='pass1234'
        )
        outsider = User.objects.create_user(
            username='other-customer', email='other-customer@example.com', password='pass1234'
        )
        Booking.objects.create(
            tour=self.tour, user=customer, booking_date=self.tour.start_date,
            name='Tour Customer', email='customer@example.com', phone='0700',
            paid=True, paid_amount=800, situation='completed',
        )
        engagement = CrewEngagement.objects.create(
            tour=self.tour, crew=self.crew, role=self.role,
            start_at=self.opportunity.start_at, end_at=self.opportunity.end_at,
            agreed_amount=Decimal('475'), status='completed',
        )
        payload = {
            'professionalism': 5, 'knowledge': 5, 'communication': 4,
            'punctuality': 5, 'safety': 5, 'overall': 5, 'comment': 'Excellent guide.',
        }
        self.client.force_login(outsider)
        self.assertEqual(
            self.client.post(reverse('tour:customer_crew_review', args=[engagement.pk]), payload).status_code,
            403,
        )
        self.client.force_login(customer)
        response = self.client.post(reverse('tour:customer_crew_review', args=[engagement.pk]), payload)
        self.assertRedirects(response, reverse('tour:customer_tours'))
        self.assertTrue(CrewReview.objects.filter(engagement=engagement, reviewer=customer).exists())

    def test_key_dashboards_render(self):
        self.client.force_login(self.moderator)
        for name in (
            'tour:operations:resource_dashboard', 'tour:operations:crew_list',
            'tour:operations:opportunity_list', 'tour:operations:engagement_list',
            'tour:operations:supplier_list', 'tour:operations:rfq_list',
            'tour:operations:service_order_list', 'tour:operations:training_list',
            'tour:operations:case_list',
        ):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.client.force_login(self.crew_user)
        self.assertEqual(self.client.get(reverse('tour:crew:dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('tour:crew:profile')).status_code, 200)

    def test_tour_resource_costs_are_grouped_by_currency(self):
        CrewEngagement.objects.create(
            tour=self.tour, crew=self.crew, role=self.role,
            start_at=self.opportunity.start_at, end_at=self.opportunity.end_at,
            agreed_amount=Decimal('475'), bonus_amount=Decimal('25'),
            currency='USD', status='confirmed',
        )
        supplier_user = User.objects.create_user(
            username='eur-supplier', email='eur-supplier@example.com', password='pass1234'
        )
        supplier = ServiceSupplier.objects.create(
            user=supplier_user, legal_name='Euro Supplier', entity_type='company',
            contact_name='Manager', phone='0700000001', status='active',
        )
        ServiceOrder.objects.create(
            order_number='SO-EUR-TEST', tour=self.tour, supplier=supplier,
            description='Transport service', start_at=self.opportunity.start_at,
            end_at=self.opportunity.end_at, quantity=1, unit='service',
            unit_price=Decimal('800'), total_amount=Decimal('800'),
            currency='EUR', status='issued', created_by=self.moderator,
        )
        self.client.force_login(self.moderator)
        response = self.client.get(reverse('tour:operations:tour_resources', args=[self.tour.pk]))
        rows = {row['currency']: row for row in response.context['financial_rows']}
        self.assertEqual(rows['USD']['total_committed'], Decimal('500'))
        self.assertEqual(rows['EUR']['total_committed'], Decimal('800'))
