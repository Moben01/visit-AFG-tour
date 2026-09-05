from django.db.models import Count
from django.utils import timezone

from .models import TourHomepageFeature


def is_feature_publication_ready(feature):
    tour = feature.tour
    try:
        duration_days = int(tour.duration_day or 0)
    except (TypeError, ValueError):
        return False

    itinerary_count = getattr(feature, "itinerary_day_count", None)
    if itinerary_count is None:
        itinerary_count = tour.itinerary_items.count()

    if not (
        feature.is_active
        and feature.physical_level
        and tour.available
        and tour.image
        and tour.title
        and tour.description
        and tour.location
        and duration_days > 0
        and itinerary_count == duration_days
    ):
        return False

    if tour.type == "schedule":
        return bool(
            tour.start_date
            and tour.end_date
            and tour.end_date >= tour.start_date >= timezone.localdate()
        )
    return tour.type == "not_schedule"


def public_featured_tours(limit=None):
    queryset = (
        TourHomepageFeature.objects.filter(
            is_active=True,
            tour__available=True,
        )
        .select_related("tour__category")
        .annotate(itinerary_day_count=Count("tour__itinerary_items", distinct=True))
        .order_by("display_order", "tour__title", "pk")
    )
    features = [feature for feature in queryset if is_feature_publication_ready(feature)]
    return features[:limit] if limit is not None else features
