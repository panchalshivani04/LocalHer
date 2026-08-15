from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SellerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('Account Credentials & Status (Uncheck Active to Block User Login)', {
            'fields': ('username', 'password', 'is_active')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')
        }),
        ('Location Details', {
            'fields': ('city', 'area', 'pincode')
        }),
        ('Platform Roles & Permissions', {
            'fields': ('is_seller', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_seller', 'is_staff', 'city')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'is_seller', 'is_staff', 'city')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    actions = ['block_and_deactivate_users', 'activate_users']

    @admin.action(description="🚫 Block & Deactivate Selected Users (Prevent Login)")
    def block_and_deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"Successfully blocked and deactivated {count} user(s). They can no longer log in.")

    @admin.action(description="✅ Activate Selected Users (Allow Login)")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {count} user(s). They can now log in normally.")


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'city', 'area', 'pincode', 'whatsapp_number', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'city')
    search_fields = ('business_name', 'user__username', 'user__email', 'city', 'area', 'pincode')
    prepopulated_fields = {'slug': ('business_name',)}
