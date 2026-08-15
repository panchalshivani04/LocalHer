from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('customers/', views.customers_list, name='customers'),
    path('sellers/', views.sellers_list, name='sellers'),
    path('businesses/', views.businesses_list, name='businesses'),
    path('products/', views.products_list, name='products'),
    path('categories/', views.categories_list, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('reports/', views.reports_list, name='reports'),
    path('blocked/', views.blocked_users_list, name='blocked'),
    path('user/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('seller/<int:seller_id>/toggle-verification/', views.toggle_seller_verification, name='toggle_seller_verification'),
    path('report/<int:report_id>/moderate/', views.moderate_report, name='moderate_report'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
]
