from django.urls import path

from . import views


app_name = "home"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("manifest.webmanifest", views.site_manifest, name="site_manifest"),
    path("search/", views.search_view, name="search"),
    path("trip-builder/", views.trip_builder_view, name="trip_builder"),
    path("my-route-requests/", views.my_trip_requests, name="my_trip_requests"),
    path(
        "route-requests/<uuid:public_id>/",
        views.trip_request_detail,
        name="trip_request_detail",
    ),
    path(
        "route-requests/<uuid:public_id>/action/",
        views.trip_request_action,
        name="trip_request_action",
    ),
    path("currency/", views.set_currency, name="set_currency"),
    path("privacy/", views.legal_page, {"page": "privacy"}, name="privacy"),
    path("terms/", views.legal_page, {"page": "terms"}, name="terms"),
    path("refunds/", views.legal_page, {"page": "refund"}, name="refund"),
]
