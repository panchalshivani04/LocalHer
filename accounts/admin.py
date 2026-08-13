from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SellerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('LocalHer Details', {'fields': ('phone_number', 'is_seller', 'city', 'area', 'pincode', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_seller', 'city', 'pincode', 'is_staff')
    list_filter = ('is_seller', 'is_staff', 'is_active', 'city')


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'city', 'area', 'pincode', 'whatsapp_number', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'city')
    search_fields = ('business_name', 'user__username', 'user__email', 'city', 'area', 'pincode')
    prepopulated_fields = {'slug': ('business_name',)}
