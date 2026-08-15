from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from .decorators import superuser_required

from accounts.models import User, SellerProfile
from marketplace.models import Category, Product, Review
from orders.models import Order
from chat.models import Report, UserBlock, Message, Conversation


@superuser_required
def dashboard_index(request):
    """
    Main Admin Command Center overview displaying real-time database statistics
    and recent platform activity streams.
    """
    customers_count = User.objects.filter(is_seller=False, is_superuser=False).count()
    sellers_count = SellerProfile.objects.count()
    products_count = Product.objects.count()
    reviews_count = Review.objects.count()
    pending_reports_count = Report.objects.filter(status='PENDING').count()
    blocked_users_count = User.objects.filter(is_active=False).count()
    orders_count = Order.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_products = Product.objects.select_related('seller', 'category').order_by('-created_at')[:5]
    pending_reports = Report.objects.select_related('reporter', 'reported_user').filter(status='PENDING').order_by('-created_at')[:5]

    context = {
        'customers_count': customers_count,
        'sellers_count': sellers_count,
        'products_count': products_count,
        'reviews_count': reviews_count,
        'pending_reports_count': pending_reports_count,
        'blocked_users_count': blocked_users_count,
        'orders_count': orders_count,
        'recent_users': recent_users,
        'recent_products': recent_products,
        'pending_reports': pending_reports,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@superuser_required
def customers_list(request):
    """
    Customer Management: View, search, and manage customer accounts.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    customers = User.objects.filter(is_superuser=False).order_by('-date_joined')

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(city__icontains=query)
        )

    if status_filter == 'active':
        customers = customers.filter(is_active=True)
    elif status_filter == 'blocked':
        customers = customers.filter(is_active=False)
    elif status_filter == 'seller':
        customers = customers.filter(is_seller=True)
    elif status_filter == 'customer':
        customers = customers.filter(is_seller=False)

    context = {
        'customers': customers,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/customers.html', context)


@superuser_required
def sellers_list(request):
    """
    Seller & Business Management: Manage seller profiles, verification status, and storefronts.
    """
    query = request.GET.get('q', '').strip()
    sellers = SellerProfile.objects.select_related('user').annotate(
        product_count=Count('products')
    ).order_by('-created_at')

    if query:
        sellers = sellers.filter(
            Q(business_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(city__icontains=query) |
            Q(area__icontains=query)
        )

    context = {
        'sellers': sellers,
        'query': query,
    }
    return render(request, 'admin_dashboard/sellers.html', context)


@superuser_required
def businesses_list(request):
    """
    Business Profile Inspector: View all registered local business profiles.
    """
    query = request.GET.get('q', '').strip()
    businesses = SellerProfile.objects.select_related('user').annotate(
        product_count=Count('products')
    ).order_by('-created_at')

    if query:
        businesses = businesses.filter(
            Q(business_name__icontains=query) |
            Q(city__icontains=query) |
            Q(area__icontains=query) |
            Q(pincode__icontains=query)
        )

    context = {
        'businesses': businesses,
        'query': query,
    }
    return render(request, 'admin_dashboard/businesses.html', context)


@superuser_required
def products_list(request):
    """
    Product Catalog Moderation: View, search, filter, and moderate products.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    products = Product.objects.select_related('seller', 'category').order_by('-created_at')

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(seller__business_name__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_id': category_id,
    }
    return render(request, 'admin_dashboard/products.html', context)


@superuser_required
def categories_list(request):
    """
    Category Management: View and add product/service categories.
    """
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    context = {
        'categories': categories,
    }
    return render(request, 'admin_dashboard/categories.html', context)


@superuser_required
def reviews_list(request):
    """
    Reviews & Ratings Moderation.
    """
    reviews = Review.objects.select_related('product', 'author').order_by('-created_at')
    context = {
        'reviews': reviews,
    }
    return render(request, 'admin_dashboard/reviews.html', context)


@superuser_required
def reports_list(request):
    """
    Incident Reports & Community Safety Queue.
    """
    reports = Report.objects.select_related('reporter', 'reported_user', 'reviewed_by').order_by('-created_at')
    context = {
        'reports': reports,
    }
    return render(request, 'admin_dashboard/reports.html', context)


@superuser_required
def blocked_users_list(request):
    """
    Blocked & Suspended Accounts Directory.
    """
    inactive_users = User.objects.filter(is_active=False).order_by('-date_joined')
    user_blocks = UserBlock.objects.select_related('blocker', 'blocked_user').order_by('-created_at')

    context = {
        'inactive_users': inactive_users,
        'user_blocks': user_blocks,
    }
    return render(request, 'admin_dashboard/blocked.html', context)


# ==========================================
# ADMIN MODERATION ACTION VIEWS
# ==========================================

@superuser_required
def toggle_user_status(request, user_id):
    """
    Toggle user active login status (Block / Restore).
    """
    user_to_mod = get_object_or_404(User, id=user_id)
    if user_to_mod.is_superuser:
        messages.error(request, "Cannot modify status of another superuser.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:customers'))

    user_to_mod.is_active = not user_to_mod.is_active
    user_to_mod.save()

    status_str = "activated (allowed login)" if user_to_mod.is_active else "blocked & deactivated (login prevented)"
    messages.success(request, f"User '{user_to_mod.username}' has been successfully {status_str}.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:customers'))


@superuser_required
def toggle_seller_verification(request, seller_id):
    """
    Toggle verification badge for a seller profile.
    """
    seller = get_object_or_404(SellerProfile, id=seller_id)
    seller.is_verified = not seller.is_verified
    seller.save()

    status_str = "Verified ✅" if seller.is_verified else "Unverified"
    messages.success(request, f"Seller '{seller.business_name}' status set to {status_str}.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:sellers'))


@superuser_required
def moderate_report(request, report_id):
    """
    Execute admin actions on submitted reports.
    """
    report = get_object_or_404(Report, id=report_id)
    action = request.POST.get('action')

    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()

    if action == 'UNDER_REVIEW':
        report.status = 'UNDER_REVIEW'
        report.admin_notes = "Marked under review by administrator."
        messages.info(request, f"Report #{report.id} marked as Under Review.")
    elif action == 'DISMISS':
        report.status = 'DISMISSED'
        report.admin_notes = "Dismissed by administrator after review."
        messages.info(request, f"Report #{report.id} dismissed.")
    elif action == 'SUSPEND':
        report.status = 'RESOLVED'
        report.reported_user.is_active = False
        report.reported_user.save()
        report.admin_notes = "Reported user account suspended platform-wide."
        messages.success(request, f"Report #{report.id} resolved. User '{report.reported_user.username}' suspended.")
    elif action == 'BLOCK':
        report.status = 'RESOLVED'
        report.reported_user.is_active = False
        report.reported_user.save()
        report.admin_notes = "Reported user permanently blocked from login."
        messages.success(request, f"Report #{report.id} resolved. User '{report.reported_user.username}' permanently blocked.")
    elif action == 'RESTORE':
        report.reported_user.is_active = True
        report.reported_user.save()
        messages.success(request, f"User '{report.reported_user.username}' access restored to Active.")

    report.save()
    return redirect('admin_dashboard:reports')


@superuser_required
def add_category(request):
    """
    Add a new product/service category.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', 'fa-tag').strip()
        if name:
            Category.objects.create(name=name, icon=icon)
            messages.success(request, f"Category '{name}' created successfully.")
        else:
            messages.error(request, "Category name is required.")
    return redirect('admin_dashboard:categories')


@superuser_required
def delete_product(request, product_id):
    """
    Remove an inappropriate product.
    """
    product = get_object_or_404(Product, id=product_id)
    title = product.title
    product.delete()
    messages.success(request, f"Product '{title}' removed from marketplace.")
    return redirect('admin_dashboard:products')


@superuser_required
def delete_review(request, review_id):
    """
    Delete an inappropriate review.
    """
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, "Review removed successfully.")
    return redirect('admin_dashboard:reviews')
