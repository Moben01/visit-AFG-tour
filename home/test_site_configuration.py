from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .admin import site_configuration_admin
from .models import Main_things


User = get_user_model()


class SiteConfigurationSingletonTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()

    def test_repeated_saves_reuse_the_single_canonical_row(self):
        first = Main_things.objects.create(hero_description="First description")
        second = Main_things(hero_description="Updated description")
        second.save()

        self.assertEqual(Main_things.objects.count(), 1)
        self.assertEqual(second.pk, first.pk)
        self.assertEqual(Main_things.get_solo().hero_description, "Updated description")
        self.assertEqual(Main_things.get_solo().singleton_key, 1)

    def test_singleton_cannot_be_deleted_through_the_model(self):
        configuration = Main_things.objects.create()

        with self.assertRaises(ValidationError):
            configuration.delete()


class SiteConfigurationValidationTests(TestCase):
    def test_invalid_email_phone_domain_and_licence_are_rejected(self):
        invalid_values = (
            ("primary_email", "not-an-email"),
            ("primary_phone", "+93 XX XXX XXXX"),
            ("primary_phone", "+93 123 456 789"),
            ("primary_domain", "https://larmoond.invalid/path"),
            ("licence_number", "TBD"),
        )
        for field_name, value in invalid_values:
            with self.subTest(field_name=field_name, value=value):
                configuration = Main_things(**{field_name: value})
                with self.assertRaises(ValidationError):
                    configuration.full_clean()

    def test_licence_fields_must_be_complete_before_badge_can_be_enabled(self):
        configuration = Main_things(
            show_licence_badge=True,
            licence_number="LT-2026-01",
        )

        with self.assertRaises(ValidationError) as context:
            configuration.full_clean()

        self.assertIn("licence_authority", context.exception.message_dict)

    def test_only_configured_public_languages_are_accepted(self):
        configuration = Main_things(active_public_languages=["en", "ps"])

        with self.assertRaises(ValidationError) as context:
            configuration.full_clean()

        self.assertIn("active_public_languages", context.exception.message_dict)

    def test_unapproved_brand_asset_extension_is_rejected(self):
        configuration = Main_things(
            logo_primary=SimpleUploadedFile("logo.txt", b"not an approved logo")
        )

        with self.assertRaises(ValidationError) as context:
            configuration.full_clean()

        self.assertIn("logo_primary", context.exception.message_dict)

    def test_hosting_services_are_limited_to_the_approved_capability_list(self):
        configuration = Main_things(
            enabled_hosting_services=["trip_consultation", "invented_service"]
        )

        with self.assertRaises(ValidationError) as context:
            configuration.full_clean()

        self.assertIn("enabled_hosting_services", context.exception.message_dict)

    def test_launch_tour_threshold_stays_within_the_supported_range(self):
        configuration = Main_things(minimum_featured_tours_for_launch=0)

        with self.assertRaises(ValidationError) as context:
            configuration.full_clean()

        self.assertIn("minimum_featured_tours_for_launch", context.exception.message_dict)


class SiteConfigurationContextTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()

    def test_configuration_is_available_to_public_templates(self):
        configuration = Main_things.objects.create(
            official_brand_name="Configuration Test Brand",
            short_brand_name="Configuration Test",
            hero_description="Configuration context marker",
            active_public_languages=["en", "fa"],
            default_currency="AFN",
        )

        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["site_config"].pk, configuration.pk)
        self.assertEqual(response.context["site_currency"], "AFN")
        self.assertEqual(
            [code for code, _label in response.context["site_public_languages"]],
            ["en", "fa"],
        )
        self.assertContains(response, "Configuration context marker")

    def test_empty_public_values_do_not_render_contact_or_asset_placeholders(self):
        Main_things.objects.create(
            hero_description="",
            legacy_domain="",
            active_public_languages=["en"],
        )

        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "info@afghanawaits.com")
        self.assertNotContains(response, 'href="mailto:')
        self.assertNotContains(response, 'href="tel:')
        self.assertNotContains(response, "brand/afghanawaits")

    def test_missing_required_values_are_reported_without_fabricated_defaults(self):
        configuration = Main_things.objects.create(hero_description="")

        self.assertFalse(configuration.is_public_ready)
        self.assertIn("hero_description", configuration.missing_required_public_fields)
        self.assertIn("primary_email", configuration.missing_required_public_fields)
        self.assertIn("logo_primary", configuration.missing_required_public_fields)

    def test_manifest_uses_configuration_and_omits_missing_icons(self):
        Main_things.objects.create(
            official_brand_name="Configuration Test Brand",
            short_brand_name="Configuration Test",
        )

        response = self.client.get(reverse("home:site_manifest"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/manifest+json")
        self.assertEqual(response.json()["name"], "Configuration Test Brand")
        self.assertNotIn("icons", response.json())

    def test_manifest_references_an_uploaded_svg_symbol(self):
        configuration = Main_things.objects.create()
        Main_things.objects.filter(pk=configuration.pk).update(
            logo_symbol="brand/icons/larmoond-symbol.svg"
        )

        response = self.client.get(reverse("home:site_manifest"))

        self.assertEqual(
            response.json()["icons"],
            [
                {
                    "src": "/media/brand/icons/larmoond-symbol.svg",
                    "sizes": "any",
                    "type": "image/svg+xml",
                    "purpose": "any",
                }
            ],
        )


class SiteConfigurationAdminTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()
        self.configuration = Main_things.objects.create(hero_description="")
        self.superuser = User.objects.create_superuser(
            username="brand-admin",
            email="brand-admin@localhost",
            password="admin-password",
        )
        self.staff_without_permission = User.objects.create_user(
            username="ordinary-staff",
            email="ordinary-staff@localhost",
            password="staff-password",
            is_staff=True,
        )
        self.configuration_manager = User.objects.create_user(
            username="configuration-manager",
            email="configuration-manager@localhost",
            password="staff-password",
            is_staff=True,
        )
        self.configuration_manager.user_permissions.add(
            Permission.objects.get(codename="manage_site_configuration")
        )
        self.change_url = reverse(
            "site_configuration_admin:home_main_things_change",
            args=(self.configuration.pk,),
        )

    def test_dedicated_admin_registers_only_site_configuration(self):
        self.assertEqual(set(site_configuration_admin._registry), {Main_things})

    def test_anonymous_user_is_redirected_to_admin_login(self):
        response = self.client.get(self.change_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("site_configuration_admin:login"), response.url)

    def test_staff_without_configuration_permission_is_forbidden(self):
        self.client.force_login(self.staff_without_permission)

        response = self.client.get(self.change_url)

        self.assertEqual(response.status_code, 403)

    def test_staff_with_configuration_permission_can_access_the_singleton(self):
        self.client.force_login(self.configuration_manager)

        response = self.client.get(self.change_url)

        self.assertEqual(response.status_code, 200)

    def test_superuser_can_access_configuration_and_sees_readiness_warning(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.change_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public-site readiness warning")
        self.assertContains(response, "Public-site setup is incomplete")

    def test_second_configuration_cannot_be_added_in_admin(self):
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("site_configuration_admin:home_main_things_add")
        )

        self.assertEqual(response.status_code, 403)

    def test_operations_contact_url_redirects_superuser_to_single_admin_source(self):
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("tour:operations:content_site_contact")
        )

        self.assertRedirects(response, self.change_url)
