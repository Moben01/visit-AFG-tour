from decimal import Decimal
from xml.etree import ElementTree

from django.test import TestCase
from django.urls import reverse

from tour.models import Tour, TourCategory

from .models import Main_things


class PublicCrawlEndpointsTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()
        Main_things.objects.create(
            primary_domain="larmoond.com",
            active_public_languages=["en", "fa"],
        )
        category = TourCategory.objects.create(
            name="Cultural tours", slug="cultural-tours", icon="ti ti-route"
        )
        tour_fields = {
            "category": category,
            "type": "not_schedule",
            "location": ["Kabul"],
            "duration_day": "5",
            "duration_night": "4",
            "price": Decimal("0"),
        }
        Tour.objects.create(
            **tour_fields,
            title="Kabul and Bamyan",
            slug="kabul-bamyan",
            description="A published journey with local guidance.",
            available=True,
        )
        Tour.objects.create(
            **tour_fields,
            title="Private draft",
            slug="private-draft",
            description="Not yet ready for travellers.",
            available=False,
        )

    def test_robots_points_to_the_canonical_sitemap(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        self.assertIn("Sitemap: https://larmoond.com/sitemap.xml", response.content.decode())

    def test_sitemap_only_lists_public_english_pages(self):
        response = self.client.get(reverse("sitemap_xml"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/xml"))
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = ElementTree.fromstring(response.content)
        locations = [node.text for node in root.findall("s:url/s:loc", namespace)]
        self.assertEqual(
            locations,
            [
                "https://larmoond.com/en/",
                "https://larmoond.com/en/trip-builder/",
                "https://larmoond.com/en/tour/tour-detail/kabul-bamyan/",
            ],
        )
        self.assertNotIn("private-draft", response.content.decode())
