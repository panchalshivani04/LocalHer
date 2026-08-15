from django.contrib import admin
from django.utils import timezone
from .models import Conversation, Message, UserBlock, Report
from accounts.models import User


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'seller', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer__username', 'seller__business_name', 'seller__user__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content_preview', 'has_image', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'content')

    def content_preview(self, obj):
        return (obj.content[:40] + '...') if len(obj.content) > 40 else obj.content
    content_preview.short_description = "Content"

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Image Attachment"


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked_user', 'created_at')
    search_fields = ('blocker__username', 'blocked_user__username')
    list_filter = ('created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'reported_user', 'user_login_status', 'reason', 'status', 'created_at', 'reviewed_by')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('reporter__username', 'reported_user__username', 'description', 'admin_notes')
    actions = ['mark_under_review', 'dismiss_reports', 'suspend_reported_user', 'block_reported_user_permanently', 'restore_reported_user']

    def user_login_status(self, obj):
        return "🟢 Active" if obj.reported_user.is_active else "🔴 Blocked / Disabled"
    user_login_status.short_description = "Reported User Login"

    @admin.action(description="Mark selected reports as Under Review")
    def mark_under_review(self, request, queryset):
        queryset.update(status='UNDER_REVIEW', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, "Selected reports marked as Under Review.")

    @admin.action(description="Dismiss selected reports")
    def dismiss_reports(self, request, queryset):
        queryset.update(status='DISMISSED', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, "Selected reports dismissed.")

    @admin.action(description="LEVEL 2 PLATFORM BAN: Suspend reported user account")
    def suspend_reported_user(self, request, queryset):
        count = 0
        for report in queryset:
            report.reported_user.is_active = False
            report.reported_user.save()
            report.status = 'RESOLVED'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.admin_notes = "Account suspended platform-wide by admin."
            report.save()
            count += 1
        self.message_user(request, f"Suspended platform access and disabled login for {count} user(s).")

    @admin.action(description="LEVEL 2 PLATFORM BAN: Block reported user account permanently")
    def block_reported_user_permanently(self, request, queryset):
        count = 0
        for report in queryset:
            report.reported_user.is_active = False
            report.reported_user.save()
            report.status = 'RESOLVED'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.admin_notes = "Account blocked permanently platform-wide by admin."
            report.save()
            count += 1
        self.message_user(request, f"Permanently blocked and disabled login for {count} user(s).")

    @admin.action(description="Restore reported user account to Active")
    def restore_reported_user(self, request, queryset):
        count = 0
        for report in queryset:
            report.reported_user.is_active = True
            report.reported_user.save()
            count += 1
        self.message_user(request, f"Restored {count} user account(s) to Active status.")
