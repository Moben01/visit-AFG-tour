from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .admin import site_configuration_admin
from .models import ContentSection, PopularPlace, ProvincePage, ProvincePageSection


User = get_user_model()


class PopularPlaceTests(TestCase):
    def setUp(self):
        PopularPlace.objects.all().update(is_active=False)
        self.dynamic_place = PopularPlace.objects.create(
            title="Database-only destination",
            province="Test province",
            description="Unique database marker",
            static_image="image_for_province/kabul.jpeg",
            url_name="states:kabul",
            display_order=10,
            is_active=True,
        )
        PopularPlace.objects.create(
            title="Hidden place",
            province="Hidden",
            description="Should not be published",
            static_image="image_for_province/kabul.jpeg",
            url_name="states:kabul",
            display_order=20,
            is_active=False,
        )

    def test_home_uses_active_database_destinations(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Database-only destination")
        self.assertNotContains(response, "Hidden place")
        self.assertIn(self.dynamic_place, response.context["destinations"])

    def test_search_filters_database_destinations(self):
        response = self.client.get(reverse("home:search"), {"q": "Unique database"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["destination_results"]),
            [self.dynamic_place],
        )

    def test_destination_is_not_managed_in_django_admin(self):
        self.assertNotIn(PopularPlace, site_configuration_admin._registry)
        response = self.client.get(reverse("site_configuration_admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("site_configuration_admin:login"), response.url)

    def test_destination_resolves_configured_url_and_image(self):
        self.assertEqual(self.dynamic_place.url, reverse("states:kabul"))
        self.assertEqual(
            self.dynamic_place.image_url,
            "/static/image_for_province/kabul.jpeg",
        )


class WebsiteContentManagementTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            username="content-moderator",
            email="moderator@example.com",
            password="test-password",
            my_choice_field="Moderator",
        )
        self.operator = User.objects.create_user(
            username="operations-user",
            email="operator@example.com",
            password="test-password",
            my_choice_field="Operator",
        )

    def test_moderator_can_open_custom_content_center(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("tour:operations:content_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Website content")
        self.assertContains(response, "Popular destinations")

    def test_all_content_management_lists_render(self):
        self.client.force_login(self.moderator)
        route_names = (
            "content_destination_list",
            "content_section_list",
            "content_province_list",
            "content_media_list",
            "content_tour_list",
            "content_category_list",
        )
        for route_name in route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(f"tour:operations:{route_name}"))
                self.assertEqual(response.status_code, 200)

    def test_moderator_cannot_edit_restricted_site_configuration(self):
        self.client.force_login(self.moderator)
        response = self.client.get(
            reverse("tour:operations:content_site_contact")
        )

        self.assertEqual(response.status_code, 403)
        for kind in ("best-places", "top-things", "attractions", "best-selling"):
            with self.subTest(kind=kind):
                response = self.client.get(
                    reverse("tour:operations:content_thing_list", args=(kind,))
                )
                self.assertEqual(response.status_code, 200)

    def test_operator_without_content_permission_is_forbidden(self):
        self.client.force_login(self.operator)
        response = self.client.get(reverse("tour:operations:content_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_moderator_can_create_destination_in_custom_panel(self):
        self.client.force_login(self.moderator)
        response = self.client.post(
            reverse("tour:operations:content_destination_create"),
            {
                "title": "Custom managed destination",
                "province": "Kabul",
                "description": "Created inside Operations Center",
                "static_image": "image_for_province/kabul.jpeg",
                "url_name": "states:kabul",
                "display_order": 44,
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("tour:operations:content_destination_list"))
        self.assertTrue(PopularPlace.objects.filter(title="Custom managed destination").exists())

    def test_published_dynamic_province_page_is_public(self):
        page = ProvincePage.objects.create(
            name="Test Province",
            slug="test-province",
            summary="Managed province summary",
            body="Managed province body",
            is_published=True,
        )
        ProvincePageSection.objects.create(
            page=page,
            heading="Managed section",
            body="Section body from the custom CMS",
            is_active=True,
        )

        response = self.client.get(page.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Managed province summary")
        self.assertContains(response, "Managed section")

    def test_homepage_sales_copy_is_not_overridden_by_legacy_section_copy(self):
        section = ContentSection.objects.get(key="home_destinations")
        section.title = "Managed homepage destination title"
        section.save(update_fields=("title", "updated_at"))

        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Places to begin your Afghanistan journey")
        self.assertNotContains(response, "Managed homepage destination title")

    def test_homepage_omits_removed_map_controls_and_currency_selector(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "data-aa-map-filter")
        self.assertNotContains(response, 'class="aa-map-trust"')
        self.assertNotContains(response, 'class="dropdown -currency"')

    def test_homepage_does_not_claim_disabled_hosting_services(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Trip consultation")
        self.assertContains(
            response,
            "Available hosting services are confirmed in writing for each journey before booking.",
        )
