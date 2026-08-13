from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem, Favorite, Order, OrderItem
from marketplace.models import Product


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product', 'product__seller')
    total_amount = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'orders/cart.html', context)


@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get custom quantity from request (default=1)
    try:
        qty = int(request.POST.get('quantity') or request.GET.get('quantity') or 1)
        if qty < 1:
            qty = 1
    except (ValueError, TypeError):
        qty = 1

    buy_now = request.POST.get('buy_now') == 'true' or request.GET.get('buy_now') == 'true'

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += qty
        cart_item.save()
        messages.info(request, f"Updated '{product.title}' quantity to {cart_item.quantity} in your cart.")
    else:
        cart_item.quantity = qty
        cart_item.save()
        messages.success(request, f"Added {qty}x '{product.title}' to your cart.")
    
    if buy_now:
        return redirect('checkout')
        
    return redirect('cart')


@login_required
def update_cart_quantity_view(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, f"Removed '{cart_item.product.title}' from your cart.")
            return redirect('cart')
    return redirect('cart')


@login_required
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_title = cart_item.product.title
    cart_item.delete()
    messages.success(request, f"Removed '{product_title}' from your cart.")
    return redirect('cart')


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product', 'product__seller')
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('marketplace')

    total_amount = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('delivery_address')
        phone = request.POST.get('contact_phone')
        notes = request.POST.get('notes', '')

        # Group items by seller so each seller gets a distinct order request
        sellers_map = {}
        for item in cart_items:
            seller = item.product.seller
            if seller not in sellers_map:
                sellers_map[seller] = []
            sellers_map[seller].append(item)

        created_orders = []
        for seller, items in sellers_map.items():
            seller_total = sum(i.total_price for i in items)
            order = Order.objects.create(
                customer=request.user,
                seller=seller,
                total_amount=seller_total,
                delivery_address=address,
                contact_phone=phone,
                notes=notes
            )
            for i in items:
                OrderItem.objects.create(
                    order=order,
                    product=i.product,
                    price=i.product.price,
                    quantity=i.quantity
                )
            created_orders.append(order)

        # Clear cart
        cart_items.delete()
        messages.success(request, "Your Order Request has been submitted successfully to the sellers!")
        return redirect('customer_orders')

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product', 'product__seller')
    return render(request, 'orders/favorites.html', {'favorites': favorites})


@login_required
def toggle_favorite_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        messages.info(request, f"Removed '{product.title}' from your saved items.")
    else:
        messages.success(request, f"Saved '{product.title}' to your favorites!")

    next_url = request.META.get('HTTP_REFERER', 'marketplace')
    return redirect(next_url)


@login_required
def customer_orders_view(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related('items__product', 'seller')
    return render(request, 'orders/customer_orders.html', {'orders': orders})
