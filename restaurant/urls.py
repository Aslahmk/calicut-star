from django.urls import path
from . import views

urlpatterns = [
    # General
    path('', views.home_view, name='home'),
    path('contact/ajax/', views.contact_ajax, name='contact_ajax'),
    path('menu/', views.menu_view, name='menu'),
    
    # Cart operations
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    
    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/payment/<int:order_id>/', views.moyasar_checkout_view, name='moyasar_checkout'),
    path('checkout/verify/', views.moyasar_verify_ajax, name='moyasar_verify'),
    
    # Receipts & Invoices
    path('order/success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('order/invoice/<int:order_id>/', views.invoice_view, name='invoice_view'),
    
    # Tracking
    path('tracking/', views.order_tracking_view, name='order_tracking'),
    
    # Dashboard
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
