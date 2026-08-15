from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User, SellerProfile


class Conversation(models.Model):
    """
    A 1-on-1 private conversation thread between a Customer and a Seller.
    Enforces uniqueness per customer-seller pair.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_conversations')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='seller_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'seller')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.customer.username} ↔ {self.seller.business_name}"

    def unread_count_for_user(self, user):
        """Returns the number of unread messages in this conversation for the given user."""
        return self.messages.exclude(sender=user).filter(is_read=False).count()

    def get_other_participant(self, user):
        """Returns details for the other participant in the conversation."""
        if user == self.customer:
            return {
                'name': self.seller.business_name,
                'subtext': f"Managed by {self.seller.user.get_full_name() or self.seller.user.username}",
                'user': self.seller.user,
                'is_seller': True,
                'avatar_letter': self.seller.business_name[0].upper() if self.seller.business_name else 'S',
                'url': f"/seller/{self.seller.slug}/"
            }
        else:
            return {
                'name': self.customer.get_full_name() or self.customer.username,
                'subtext': 'Local Customer',
                'user': self.customer,
                'is_seller': False,
                'avatar_letter': (self.customer.first_name or self.customer.username)[0].upper(),
                'url': '#'
            }


class Message(models.Model):
    """
    Individual chat message within a Conversation.
    Supports text content and optional photo uploads.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg from {self.sender.username} at {self.timestamp.strftime('%H:%M')}"


class UserBlock(models.Model):
    """
    LEVEL 1 PERSONAL BLOCK:
    Represents a personal block between two users.
    Prevents direct messaging and conversation creation between blocker and blocked_user.
    Does NOT ban the user from the rest of the platform.
    """
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked_user')
        ordering = ['-created_at']

    def clean(self):
        if self.blocker == self.blocked_user:
            raise ValidationError("You cannot block yourself.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked_user.username}"


class Report(models.Model):
    """
    LEVEL 2 MODERATION REPORT:
    Safety report submitted by customers or sellers for admin review.
    """
    REASON_CHOICES = [
        ('HARASSMENT', 'Harassment or Abusive Behavior'),
        ('INAPPROPRIATE', 'Inappropriate Content'),
        ('SPAM', 'Spam or Unwanted Messages'),
        ('THREAT', 'Threatening Behavior'),
        ('SCAM', 'Scam or Fraud Attempt'),
        ('MISLEADING', 'Fake Business or Misleading Info'),
        ('OTHER', 'Other Inappropriate Behavior'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='filed_reports')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reports')
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default='OTHER')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id}: {self.reporter.username} -> {self.reported_user.username} ({self.get_reason_display()})"
