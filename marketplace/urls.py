from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('search/', views.search_view, name='search'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('seller/<slug:slug>/', views.seller_profile_view, name='seller_profile'),
    path('review/add/<int:product_id>/', views.add_review_view, name='add_review'),
]
