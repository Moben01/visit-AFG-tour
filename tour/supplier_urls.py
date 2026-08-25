from django.urls import path

from . import resource_views as views

app_name = 'supplier'

urlpatterns = [
    path('onboarding/', views.supplier_onboarding, name='onboarding'),
    path('', views.supplier_dashboard, name='dashboard'),
    path('profile/', views.supplier_profile, name='profile'),
    path('profile/services/add/', views.supplier_service_add, name='service_add'),
    path('profile/assets/add/', views.supplier_asset_add, name='asset_add'),
    path('profile/documents/add/', views.supplier_document_add, name='document_add'),
    path('rfqs/', views.supplier_rfq_list, name='rfqs'),
    path('rfqs/<int:rfq_id>/', views.supplier_rfq_detail, name='rfq_detail'),
    path('orders/', views.supplier_order_list, name='orders'),
    path('orders/<int:order_id>/', views.supplier_order_detail, name='order_detail'),
    path('orders/<int:order_id>/action/', views.supplier_order_action, name='order_action'),
    path('orders/<int:order_id>/invoices/add/', views.supplier_invoice_add, name='invoice_add'),
]
