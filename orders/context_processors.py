from .models import CartItem

def cart_processor(request):
    """
    Makes cart item count dynamically available across all HTML templates.
    """
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_count': count}
