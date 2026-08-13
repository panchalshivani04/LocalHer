from django.db import models
from accounts.models import User, SellerProfile
from marketplace.models import Product


class CartItem(models.Model):
    """
    Items added to customer shopping cart.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_carts')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.title} in {self.user.username}'s cart"


class Favorite(models.Model):
    """
    Saved/Favorite products wishlist for customers.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.title}"


class Order(models.Model):
    """
    Order Request submitted by a Customer to a Seller.
    Status flow: PENDING -> ACCEPTED -> FULFILLED (or CANCELLED).
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Seller Confirmation'),
        ('ACCEPTED', 'Accepted by Seller'),
        ('FULFILLED', 'Order Fulfilled'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_placed')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='orders_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    contact_phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True, help_text="Special instructions or service customization notes.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.customer.username} -> {self.seller.business_name} ({self.status})"


class OrderItem(models.Model):
    """
    Individual item in an Order Request.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.title if self.product else 'Item'} in Order #{self.order.id}"
