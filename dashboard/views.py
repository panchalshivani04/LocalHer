from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from marketplace.models import Product, ProductImage, Category
from orders.models import Order
from accounts.models import SellerProfile


@login_required
def seller_dashboard_view(request):
    """
    Main Seller Dashboard Command Center.
    Requires seller profile.
    """
    if not request.user.is_seller or not hasattr(request.user, 'seller_profile'):
        messages.warning(request, "Please register your business profile to access the Seller Dashboard.")
        return redirect('register_seller')

    seller = request.user.seller_profile
    products = seller.products.all().select_related('category').prefetch_related('images')
    orders = seller.orders_received.all().select_related('customer').prefetch_related('items__product')

    # Metrics
    total_products = products.count()
    total_orders = orders.count()
    pending_orders = orders.filter(status='PENDING').count()
    
    # Calculate average rating across seller products
    all_reviews = [r for p in products for r in p.reviews.select_related('author', 'product').all()]
    avg_rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 1) if all_reviews else 0.0

    context = {
        'seller': seller,
        'products': products,
        'orders': orders,
        'reviews': all_reviews,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'avg_rating': avg_rating,
        'total_reviews': len(all_reviews),
    }
    return render(request, 'dashboard/seller_dashboard.html', context)


@login_required
def seller_product_add_view(request):
    if not request.user.is_seller:
        return redirect('register_seller')

    seller = request.user.seller_profile
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        price_unit = request.POST.get('price_unit', 'per item')
        product_type = request.POST.get('product_type', 'PRODUCT')
        is_available = request.POST.get('is_available') == 'on'

        category = get_object_or_404(Category, id=category_id)
        
        product = Product.objects.create(
            seller=seller,
            category=category,
            title=title,
            description=description,
            price=price,
            price_unit=price_unit,
            product_type=product_type,
            is_available=is_available,
            city=seller.city,
            area=seller.area,
            pincode=seller.pincode
        )

        # Handle multiple uploaded images
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(idx == 0)
            )

        messages.success(request, f"Listing '{product.title}' created successfully!")
        return redirect('seller_dashboard')

    return render(request, 'dashboard/product_form.html', {'categories': categories, 'action': 'Add'})


@login_required
def seller_product_edit_view(request, pk):
    if not request.user.is_seller:
        return redirect('register_seller')

    seller = request.user.seller_profile
    product = get_object_or_404(Product, pk=pk, seller=seller)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.title = request.POST.get('title')
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, id=category_id)
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.price_unit = request.POST.get('price_unit')
        product.product_type = request.POST.get('product_type')
        product.is_available = request.POST.get('is_available') == 'on'
        product.save()

        # Upload additional images if provided
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(product.images.count() == 0 and idx == 0)
            )

        messages.success(request, f"Listing '{product.title}' updated successfully!")
        return redirect('seller_dashboard')

    return render(request, 'dashboard/product_form.html', {'product': product, 'categories': categories, 'action': 'Edit'})


@login_required
def seller_product_delete_view(request, pk):
    if not request.user.is_seller:
        return redirect('register_seller')

    seller = request.user.seller_profile
    product = get_object_or_404(Product, pk=pk, seller=seller)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        messages.success(request, f"Deleted product '{product_title}'.")
        return redirect('seller_dashboard')

    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


@login_required
def seller_order_status_view(request, order_id):
    if not request.user.is_seller:
        return redirect('register_seller')

    seller = request.user.seller_profile
    order = get_object_or_404(Order, id=order_id, seller=seller)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        current_status = order.status

        # Strict Sequential Workflow Checks
        valid_transition = False
        if current_status == 'PENDING' and new_status in ['ACCEPTED', 'CANCELLED']:
            valid_transition = True
        elif current_status == 'ACCEPTED' and new_status in ['FULFILLED', 'CANCELLED']:
            valid_transition = True

        if valid_transition:
            order.status = new_status
            order.save()
            messages.success(request, f"Updated Order #{order.id} status to {order.get_status_display()}.")

            # Automatically notify Customer in Chat thread
            try:
                from chat.models import Conversation, Message
                conv, _ = Conversation.objects.get_or_create(customer=order.customer, seller=seller)
                
                if new_status == 'ACCEPTED':
                    status_text = f"✅ ORDER #{order.id} ACCEPTED!\nThe seller has accepted your order request."
                elif new_status == 'FULFILLED':
                    status_text = f"🎉 ORDER #{order.id} COMPLETED & FULFILLED!\nYour order is fulfilled. Please leave a review to support the seller!"
                elif new_status == 'CANCELLED':
                    status_text = f"❌ ORDER #{order.id} CANCELLED\nThe order request has been cancelled by the seller."
                else:
                    status_text = f"ℹ️ ORDER #{order.id} Status Updated: {order.get_status_display()}"

                Message.objects.create(
                    conversation=conv,
                    sender=request.user,
                    content=status_text
                )
                conv.save()
            except Exception:
                pass
        else:
            messages.warning(request, f"Invalid status transition for Order #{order.id}.")

    return redirect('seller_dashboard')


@login_required
def seller_product_toggle_availability_view(request, pk):
    if not request.user.is_seller:
        return redirect('register_seller')
    seller = request.user.seller_profile
    product = get_object_or_404(Product, pk=pk, seller=seller)
    product.is_available = not product.is_available
    product.save()
    status_str = "In Stock / Available" if product.is_available else "Out of Stock"
    messages.success(request, f"Updated '{product.title}' status to '{status_str}'.")
    return redirect('seller_dashboard')

