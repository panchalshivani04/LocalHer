from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    """
    Custom User Model supporting both Normal Customers and Sellers.
    Every user is a customer by default. Sellers have is_seller=True
    and an associated SellerProfile.
    """
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact phone number")
    is_seller = models.BooleanField(default=False, help_text="Designates whether the user runs a business on LocalHer.")
    city = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/users/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({'Seller' if self.is_seller else 'Customer'})"


class SellerProfile(models.Model):
    """
    Business Profile associated with a User who acts as a Seller.
    Contains business details, location, cover image, and contact information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    bio = models.TextField(blank=True, help_text="Short description of your business and story.")
    cover_image = models.ImageField(upload_to='profiles/sellers/covers/', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, help_text="WhatsApp number for direct customer orders/inquiries.")
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False, help_text="Admin verification badge for trust.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.business_name)
            slug = base_slug
            counter = 1
            while SellerProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.business_name} ({self.user.get_full_name() or self.user.username})"
