from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_quantity_view, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite_view, name='toggle_favorite'),
    path('my-orders/', views.customer_orders_view, name='customer_orders'),
    path('order/<int:order_id>/cancel/', views.cancel_order_view, name='cancel_order'),
]
