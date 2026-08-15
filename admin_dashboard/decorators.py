from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def superuser_required(view_func):
    """
    Decorator enforcing that only authenticated superuser administrators
    can access custom admin dashboard views. Non-superusers are safely blocked
    and redirected with a clear warning message.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in with administrator credentials to access the admin portal.")
            return redirect('login')
        
        if not request.user.is_superuser:
            messages.error(request, "⛔ Access Denied. You do not have administrator permissions to access the LocalHer Admin Dashboard.")
            if getattr(request.user, 'is_seller', False):
                return redirect('seller_dashboard')
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
