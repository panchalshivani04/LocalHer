from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Review
from accounts.models import SellerProfile


def home_view(request):
    """
    Main Marketplace Home for Logged-In Users.
    Displays Hyperlocal discovery banner, Category grid, and Product feed.
    """
    categories = Category.objects.all()
    user_pincode = getattr(request.user, 'pincode', None)
    
    # Prioritize products in user's area/pincode if set
    products = Product.objects.filter(is_available=True).select_related('seller', 'category')
    if user_pincode:
        nearby_products = products.filter(pincode=user_pincode)
        other_products = products.exclude(pincode=user_pincode)
        products = list(nearby_products) + list(other_products)

    sellers = SellerProfile.objects.all()[:6]

    context = {
        'categories': categories,
        'products': products[:12],
        'sellers': sellers,
    }
    return render(request, 'marketplace/home.html', context)


def marketplace_view(request):
    """
    Explore Marketplace page with Category, Location & Price Filters + Sorting.
    """
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True).select_related('seller', 'category')

    # Filtering parameters
    cat_slug = request.GET.get('category')
    p_type = request.GET.get('type')
    city = request.GET.get('city')
    pincode = request.GET.get('pincode')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if cat_slug:
        products = products.filter(category__slug=cat_slug)
    if p_type in ['PRODUCT', 'SERVICE']:
        products = products.filter(product_type=p_type)
    if city:
        products = products.filter(city__icontains=city)
    if pincode:
        products = products.filter(pincode=pincode)
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    context = {
        'categories': categories,
        'products': products,
        'selected_category': cat_slug,
        'selected_type': p_type,
        'selected_max_price': max_price,
        'selected_sort': sort,
    }
    return render(request, 'marketplace/explore.html', context)


def search_view(request):
    """
    Unified Search across Product title/description, Seller business name, and Category name.
    """
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    sellers = SellerProfile.objects.none()

    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).filter(is_available=True).select_related('seller', 'category')

        sellers = SellerProfile.objects.filter(
            Q(business_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(city__icontains=query) |
            Q(area__icontains=query)
        )

    context = {
        'query': query,
        'products': products,
        'sellers': sellers,
    }
    return render(request, 'marketplace/search_results.html', context)


def product_detail_view(request, slug):
    """
    Product or Service Detail Page with image gallery, seller bio, and customer reviews.
    """
    product = get_object_or_404(Product.objects.select_related('seller', 'category'), slug=slug)
    related_products = Product.objects.filter(category=product.category, is_available=True).exclude(pk=product.pk)[:4]
    reviews = product.reviews.select_related('author')

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    }
    return render(request, 'marketplace/product_detail.html', context)


def seller_profile_view(request, slug):
    """
    Public Seller Storefront displaying business details, location, and listed products.
    """
    seller = get_object_or_404(SellerProfile, slug=slug)
    products = seller.products.filter(is_available=True).select_related('category')
    
    # Dynamically extract categories this seller has products in
    categories = Category.objects.filter(products__seller=seller).distinct()

    context = {
        'seller': seller,
        'products': products,
        'categories': categories,
    }
    return render(request, 'marketplace/seller_profile.html', context)


@login_required
def add_review_view(request, product_id):
    """
    Submit or update a 1-5 star rating and written review for a product.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 5))
        except (ValueError, TypeError):
            rating = 5

        comment = request.POST.get('comment', '').strip()
        if comment:
            Review.objects.update_or_create(
                product=product,
                author=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, f"Thank you! Your {rating}★ review for '{product.title}' has been submitted.")
        else:
            messages.error(request, "Please write a short comment with your rating.")
    
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('customer_orders')


def privacy_policy_view(request):
    """
    Renders Privacy Policy page detailing data minimization & protection.
    """
    return render(request, 'privacy_policy.html')


def terms_view(request):
    """
    Renders Terms of Service page.
    """
    return render(request, 'terms.html')


def safety_view(request):
    """
    Renders Safety & Moderation Guidelines page.
    """
    return render(request, 'safety.html')

