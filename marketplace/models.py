from django.db import models
from django.utils.text import slugify
from accounts.models import User, SellerProfile


class Category(models.Model):
    """
    Marketplace Business/Product Categories (e.g., Food & Pickles, Tailoring & Embroidery, Baking, Crafts).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, default='fa-tag', help_text="FontAwesome icon class e.g. fa-utensils, fa-scissors")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Unified Product & Service Model listed by Sellers.
    Supports both tangible goods (pickles, jewellery) and local services (tailoring, tuition, mehendi).
    """
    PRODUCT_TYPES = (
        ('PRODUCT', 'Physical Product'),
        ('SERVICE', 'Local Service'),
    )

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=230, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=50, default='per item', help_text="e.g. per piece, per kg, per hour, starting price")
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='PRODUCT')
    is_available = models.BooleanField(default=True, help_text="Available for order/booking")
    
    # Location fields for hyperlocal discovery
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Sync location from seller if missing
        if self.seller and not self.city:
            self.city = self.seller.city
            self.area = self.seller.area
            self.pincode = self.seller.pincode
            
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        first_img = self.images.first()
        return first_img.image if first_img else None

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0

    @property
    def total_reviews(self):
        return self.reviews.count()

    def __str__(self):
        return f"{self.title} — ₹{self.price} ({self.seller.business_name})"


class ProductImage(models.Model):
    """
    Multiple Images per Product/Service listing.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"


class Review(models.Model):
    """
    Ratings (1 to 5 stars) & written reviews submitted by Customers for a Product/Service.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'author')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ by {self.author.username} on {self.product.title}"
