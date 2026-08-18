from .models import CartItem, Favorite

def cart_processor(request):
    """
    Makes cart item count and user favorite product IDs dynamically available across all HTML templates.
    """
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        cart_count = 0
        favorite_ids = set()
    return {
        'cart_count': cart_count,
        'user_favorite_product_ids': favorite_ids,
    }
