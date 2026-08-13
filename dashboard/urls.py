from django.urls import path
from . import views

urlpatterns = [
    path('seller/', views.seller_dashboard_view, name='seller_dashboard'),
    path('seller/product/add/', views.seller_product_add_view, name='seller_product_add'),
    path('seller/product/edit/<int:pk>/', views.seller_product_edit_view, name='seller_product_edit'),
    path('seller/product/delete/<int:pk>/', views.seller_product_delete_view, name='seller_product_delete'),
    path('seller/product/toggle/<int:pk>/', views.seller_product_toggle_availability_view, name='seller_product_toggle'),
    path('seller/order/status/<int:order_id>/', views.seller_order_status_view, name='seller_order_status'),
]
