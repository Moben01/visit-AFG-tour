from django.urls import path

from . import views


app_name = "home"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("search/", views.search_view, name="search"),
    path("currency/", views.set_currency, name="set_currency"),
    path("privacy/", views.legal_page, {"page": "privacy"}, name="privacy"),
    path("terms/", views.legal_page, {"page": "terms"}, name="terms"),
    path("refunds/", views.legal_page, {"page": "refund"}, name="refund"),
]
