"""Small public crawl endpoints, outside the language-prefixed URL patterns."""

from xml.etree import ElementTree

from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import override
from django.views.decorators.http import require_GET

from tour.models import Tour

from .models import Main_things


SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ElementTree.register_namespace("", SITEMAP_NS)


def _site_origin(request):
    return Main_things.get_solo().canonical_origin or request.build_absolute_uri("/").rstrip("/")


@require_GET
def robots_txt(request):
    response = HttpResponse(
        f"User-agent: *\nAllow: /\n\nSitemap: {_site_origin(request)}/sitemap.xml\n",
        content_type="text/plain; charset=utf-8",
    )
    response["Cache-Control"] = "public, max-age=300"
    return response


@require_GET
def sitemap_xml(request):
    """List English pages with a public route; never list private or preview URLs."""
    origin = _site_origin(request)
    root = ElementTree.Element(f"{{{SITEMAP_NS}}}urlset")

    with override("en"):
        paths = [reverse("home:home"), reverse("home:trip_builder")]
        paths.extend(
            reverse("tour:tour_details", kwargs={"slug": slug})
            for slug in Tour.objects.filter(available=True)
            .exclude(slug="")
            .exclude(description="")
            .order_by("slug")
            .values_list("slug", flat=True)
        )

    for path in paths:
        url = ElementTree.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ElementTree.SubElement(url, f"{{{SITEMAP_NS}}}loc").text = f"{origin}{path}"

    response = HttpResponse(
        ElementTree.tostring(root, encoding="utf-8", xml_declaration=True),
        content_type="application/xml; charset=utf-8",
    )
    response["Cache-Control"] = "public, max-age=300"
    return response
