from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomerRegistrationForm, SellerRegistrationForm, UserProfileForm
from .models import SellerProfile
from marketplace.models import Category, Product


def landing_view(request):
    """
    Public landing page featuring platform introduction, featured categories,
    and call to action for customers and sellers.
    """
    if request.user.is_authenticated:
        return redirect('home')

    categories = Category.objects.all()[:8]
    featured_products = Product.objects.filter(is_available=True).select_related('seller', 'category')[:6]
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'landing.html', context)


def register_view(request):
    """
    Register a standard Customer account.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_seller = False
            user.save()
            
            login(request, user)
            messages.success(request, f"Welcome to LocalHer, {user.first_name or user.username}! Your customer account is ready.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form, 'role': 'customer'})


def register_seller_view(request):
    """
    Register a Seller account (Creates User + SellerProfile in one flow).
    """
    if request.user.is_authenticated and not request.user.is_seller:
        # User already exists as customer, converting to seller
        if request.method == 'POST':
            business_name = request.POST.get('business_name')
            whatsapp = request.POST.get('whatsapp_number', '')
            bio = request.POST.get('bio', '')
            if business_name:
                seller_profile = SellerProfile.objects.create(
                    user=request.user,
                    business_name=business_name,
                    whatsapp_number=whatsapp or request.user.phone_number,
                    bio=bio,
                    city=request.user.city or 'Local',
                    area=request.user.area or 'Neighborhood',
                    pincode=request.user.pincode or '000000'
                )
                request.user.is_seller = True
                request.user.save()
                messages.success(request, f"Congratulations! Your business '{business_name}' is now registered on LocalHer.")
                return redirect('seller_dashboard')
            else:
                messages.error(request, "Business Name is required.")
        return render(request, 'accounts/register_seller_existing.html')

    if request.user.is_authenticated and request.user.is_seller:
        return redirect('seller_dashboard')

    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_seller = True
            user.save()

            # Create SellerProfile
            SellerProfile.objects.create(
                user=user,
                business_name=form.cleaned_data['business_name'],
                whatsapp_number=form.cleaned_data['whatsapp_number'] or user.phone_number,
                bio=form.cleaned_data['bio'],
                city=user.city,
                area=user.area,
                pincode=user.pincode
            )

            login(request, user)
            messages.success(request, f"Welcome to LocalHer, {user.first_name}! Your seller profile '{form.cleaned_data['business_name']}' has been created.")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Please fix the errors in the form below.")
    else:
        form = SellerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form, 'role': 'seller'})


def login_view(request):
    """
    Standard user login view.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Handle Remember Me checkbox (14 days expiry vs session close)
            remember_me = request.POST.get('remember_me')
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Expires on browser close

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_seller:
                return redirect('seller_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')


from .forms import CustomerRegistrationForm, SellerRegistrationForm, UserProfileForm, SellerProfileForm

@login_required
def profile_view(request):
    seller_form = None
    seller_profile = getattr(request.user, 'seller_profile', None)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if request.user.is_seller and seller_profile:
            seller_form = SellerProfileForm(request.POST, request.FILES, instance=seller_profile)
        
        user_valid = user_form.is_valid()
        seller_valid = seller_form.is_valid() if seller_form else True

        if user_valid and seller_valid:
            user_form.save()
            if seller_form:
                seller_form.save()
            messages.success(request, "Your account & storefront details have been updated successfully.")
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        if request.user.is_seller and seller_profile:
            seller_form = SellerProfileForm(instance=seller_profile)

    context = {
        'form': user_form,
        'seller_form': seller_form,
    }
    return render(request, 'accounts/profile.html', context)
