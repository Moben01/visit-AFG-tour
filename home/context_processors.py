from django.db import DatabaseError

from tour.models import TourCategory, User_favorite_tour


def site_navigation(request):
    try:
        categories = TourCategory.objects.all()[:12]
        favorite_count = (
            User_favorite_tour.objects.filter(user=request.user, favorite=True).count()
            if request.user.is_authenticated
            else 0
        )
    except DatabaseError:
        categories = ()
        favorite_count = 0

    return {
        "get_tour_categories": categories,
        "find_user_favorite": favorite_count,
        "site_currency": request.session.get("currency", "USD"),
    }
