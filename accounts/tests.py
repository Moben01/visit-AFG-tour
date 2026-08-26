from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from allauth.account.models import EmailAddress


User = get_user_model()


class EmailAuthenticationTests(TestCase):
    password = 'StrongEmailLogin#2026'

    def create_verified_user(self, email='traveler@example.com'):
        user = User.objects.create_user(
            username='internal-traveler', email=email, password=self.password
        )
        EmailAddress.objects.create(
            user=user, email=email, primary=True, verified=True
        )
        return user

    def test_signup_form_uses_email_without_username(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].fields)
        self.assertNotIn('username', response.context['form'].fields)
        self.assertContains(response, 'type="email"')

    def test_signup_requires_email_verification(self):
        response = self.client.post(reverse('account_signup'), {
            'email': 'New.Traveler@Example.com',
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='new.traveler@example.com')
        address = EmailAddress.objects.get(user=user)
        self.assertFalse(address.verified)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('confirm', mail.outbox[0].body.lower())

    def test_verification_sent_page_uses_designed_account_state(self):
        response = self.client.get(reverse('account_email_verification_sent'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aa-verification-card')
        self.assertContains(response, 'aa-verification-steps')
        self.assertContains(response, reverse('account_login'))

    def test_verified_user_logs_in_with_email(self):
        user = self.create_verified_user()
        response = self.client.post(reverse('account_login'), {
            'login': 'TRAVELER@EXAMPLE.COM', 'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_unverified_email_cannot_log_in(self):
        user = User.objects.create_user(
            username='unverified-internal',
            email='unverified@example.com',
            password=self.password,
        )
        EmailAddress.objects.create(
            user=user, email=user.email, primary=True, verified=False
        )
        response = self.client.post(reverse('account_login'), {
            'login': user.email, 'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_duplicate_email_signup_is_rejected_case_insensitively(self):
        self.create_verified_user('member@example.com')
        response = self.client.post(reverse('account_signup'), {
            'email': 'MEMBER@EXAMPLE.COM',
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            User.objects.filter(email__iexact='member@example.com').count(), 1
        )
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_username_is_not_accepted_for_public_login(self):
        self.create_verified_user()
        response = self.client.post(reverse('account_login'), {
            'login': 'internal-traveler', 'password': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_email_is_case_insensitively_unique(self):
        self.create_verified_user('unique@example.com')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username='another-internal-user',
                    email='UNIQUE@EXAMPLE.COM',
                    password=self.password,
                )
